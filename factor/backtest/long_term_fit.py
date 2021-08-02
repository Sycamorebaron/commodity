import sys
import os
import pandas as pd
from multiprocessing import Pool
from sklearn import decomposition
from sklearn.ensemble import RandomForestRegressor
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import numpy as np
import time
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from factor.backtest.syn_test_hf import HFSynTest
from utils.base_para import local_data_path, local_15t_factor_path, NORMAL_CONTRACT_INFO

pd.set_option('expand_frame_repr', False)


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, 'Timer', round(end-start, 4))
        return res
    return wrapper


class LongTermTest(HFSynTest):
    def __init__(
            self, factor_name, begin_date, end_date, init_cash, contract_list, local_factor_data_path, local_data_path,
            term, leverage, train_data_len
    ):
        HFSynTest.__init__(
            self, factor_name, begin_date, end_date, init_cash, contract_list, local_factor_data_path, local_data_path,
            term, leverage, train_data_len
        )
        self.use_factor_list = []
        self.last_update_date = pd.to_datetime('2000-01-01')

    def _t_factor_list(self, comm_factor):
        return self.use_factor_list

    def form_comm_factor(self, use_days=90):
        comm_factor = {}
        for comm in self.open_comm:
            t_comm_d = self.comm_factor_data[comm].loc[
                (self.comm_factor_data[comm]['datetime'] < self.agent.earth_calender.now_date) &
                (self.comm_factor_data[comm]['datetime'] >=
                 (self.agent.earth_calender.now_date - timedelta(days=use_days)))
            ]
            comm_factor[comm] = t_comm_d.reset_index(drop=True)
        return comm_factor

    def long_term_update_factor_list(self, comm_factor):
        """
        选择累计IC距离前50%的因子
        :param comm_factor:
        :return:
        """
        factor_t_exp_ic_dist = {}

        for factor in self.factor.keys():
            factor_df = pd.DataFrame()
            for comm in comm_factor:
                comm_f_data = comm_factor[comm][['datetime', factor, '15Tf_rtn']]
                comm_f_data.columns = ['datetime', comm, '%s_f_rtn' % comm]
                if len(factor_df):
                    factor_df = factor_df.merge(comm_f_data, on='datetime', how='outer')
                else:
                    factor_df = comm_f_data
            factor_df = factor_df[-2-self.train_data_len: -1].copy().reset_index(drop=True)

            factor_t_exp_ic_dist[factor] = self._factor_exp_ic_dist(factor=factor, factor_df=factor_df)

        factor_t_exp_ic_dist_df = pd.DataFrame(factor_t_exp_ic_dist, index=['exp_ic_dist']).T

        factor_list = list(factor_t_exp_ic_dist_df.loc[
            factor_t_exp_ic_dist_df['exp_ic_dist'] >= factor_t_exp_ic_dist_df['exp_ic_dist'].median()
        ].index)

        return factor_list

    def update_use_factor_list_if_must(self):
        # 每30天更新一次
        if (self.agent.earth_calender.now_date - self.last_update_date)  > timedelta(days=30):
            # 使用过去90天的数据更新
            comm_factor = self.form_comm_factor(use_days=90)
            t_factor_list = self.long_term_update_factor_list(comm_factor=comm_factor)
            self.last_update_date = self.agent.earth_calender.now_date
            self.use_factor_list = t_factor_list
            print('update factors: ', self.use_factor_list)

    def _daily_process(self):
        self.open_comm = self._open_comm()
        self.update_use_factor_list_if_must()
        HFSynTest._daily_process(self)

    def _termly_process_skip_rest(self, term_begin_time):
        """
        每期进行的流程
        :param term_begin_time:
        :return:
        """

        # 先平仓
        close_pos = {}
        for comm in self.exchange.account.position.holding_position.keys():
            for contract in self.exchange.account.position.holding_position[comm].keys():
                close_pos[contract] = 0
        if len(close_pos):
            print('close', term_begin_time)

            close_trade_info = self.agent.change_position(
                exchange=self.exchange,
                target_pos=close_pos,
                now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time),
                field='close',
            )
            self.exchange.account.equity = self.exchange.account.cash
            self.agent.recorder.record_trade(info=close_trade_info)

        if term_begin_time not in ['09:01', '10:01', '10:16', '10:31', '13:01', '21:01']:

            # 再开仓
            target_pos = self.strategy_target_pos(
                now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time)
            )

            # 根据目标仓位调仓
            open_trade_info = self.agent.change_position(
                exchange=self.exchange,
                target_pos=target_pos,
                now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time),
                field='open'
            )

    @timer
    def strategy_target_pos(self, now_dt):
        comm_factor = self.form_train_data(now_dt=now_dt)
        t_factor_list = self._t_factor_list(comm_factor)
        # print('t_factor_list', t_factor_list)
        mp_data_set = []
        for comm in comm_factor.keys():
            t_comm_data = comm_factor[comm][['15Tf_rtn'] + t_factor_list][-1-self.train_data_len:]
            for col in [i for i in t_comm_data.columns if i != '15Tf_rtn']:
                t_comm_data[col] = (t_comm_data[col] - t_comm_data[col].mean()) / t_comm_data[col].std(ddof=1)

            train_data = t_comm_data[:-1].dropna(how='any')
            test_data = t_comm_data.iloc[-1]

            # cal_factor data 中有因子缺失，需要在训练数据中也将这部分因子去掉
            if np.isnan(test_data[1:]).any():
                test_miss_col = [i for i in test_data.index if np.isnan(test_data[i])]
                if '15Tf_rtn' in test_miss_col:
                    test_miss_col.remove('15Tf_rtn')

                t_comm_data = t_comm_data[[i for i in t_comm_data.columns if i not in test_miss_col]]
                train_data = t_comm_data[:-1].dropna(how='any')
                test_data = t_comm_data.iloc[-1]

            if len(train_data.columns) <= 1 :
                print(comm, 'pass')
                continue
            else:
                mp_data_set.append(
                    {
                        'comm': comm,
                        'train_data': train_data,
                        'test_data': test_data
                    }
                )
        # -------------------------------------多进程------------------------------------------
        # pool = Pool(processes=4)
        # jobs = []
        # for dataset in mp_data_set:
        #     jobs.append(pool.apply_async(
        #         self.mp_pred_rtn_xgboost, (dataset['comm'], dataset['train_data'], dataset['test_data'])
        #     ))
        # pool.close()
        # pool.join()
        # res_list = [j.get() for j in jobs]

        # ------------------------------------------------------------------------------------

        # -------------------------------------循环------------------------------------------
        res_list = []
        for dataset in mp_data_set:
            res_list.append(self.mp_pred_rtn_xgboost(dataset['comm'], dataset['train_data'], dataset['test_data']))

        # -----------------------------------------------------------------------------------
        res_df = pd.DataFrame(res_list).sort_values(by='pred_res')
        if (res_df['pred_res'].iloc[-1] - res_df['pred_res'].iloc[0]) > 0.004:
            signal = {
                self.exchange.contract_dict[res_df['comm'].iloc[0]].now_main_contract(
                    now_date=self.agent.earth_calender.now_date): -0.5,
                self.exchange.contract_dict[res_df['comm'].iloc[-1]].now_main_contract(
                    now_date=self.agent.earth_calender.now_date): 0.5
            }
        else:
            signal = {}
        print(now_dt, signal)
        return signal


class PCADeCorrLongTermTest(HFSynTest):
    def __init__(
            self, factor_name, begin_date, end_date, init_cash, contract_list, local_factor_data_path, local_data_path,
            term, leverage, train_data_len
    ):
        HFSynTest.__init__(
            self, factor_name, begin_date, end_date, init_cash, contract_list, local_factor_data_path, local_data_path,
            term, leverage, train_data_len
        )
        self.components = {}
        self.last_update_date = pd.to_datetime('2000-01-01')
        self.signals = []

    def form_factor_data(self):
        print('REFROM FACTORS...')
        comm_factor = {}
        for comm in self.exchange.contract_dict.keys():
            print(comm)
            _comm_d = pd.DataFrame()
            for factor in self.factor.keys():
                _comm_f = self.factor[factor][['datetime', comm]]
                _comm_f.columns = ['datetime', factor]
                if len(_comm_d):
                    _comm_d = _comm_d.merge(_comm_f, on='datetime', how='outer')
                else:
                    _comm_d = _comm_f

            _comm_d.sort_values(by='datetime', ascending=True, inplace=True)
            cond1 = _comm_d['datetime'].dt.hour >= 9
            cond2 = _comm_d['datetime'].dt.hour <= 15
            _comm_d = _comm_d.loc[cond1 & cond2]

            _comm_d.reset_index(drop=True, inplace=True)
            _comm_d['15Tf_rtn'] = _comm_d['15Thf_rtn'].shift(-1)
            _comm_d[[i for i in _comm_d.columns if i not in ['datetime', '15Tf_rtn']]] = \
                _comm_d[[i for i in _comm_d.columns if i not in ['datetime', '15Tf_rtn']]].fillna(method='ffill')
            comm_factor[comm] = _comm_d


        return comm_factor

    def renew_pca_components(self, comm_factor):
        """
        PCA对因子进行线性不相关处理
        :param comm_factor:
        :return:
        """
        print(comm_factor.keys())
        comm_components = {}
        for comm in comm_factor.keys():

            print('renew component', comm)
            d = comm_factor[comm]
            d = d[[i for i in d.columns if i not in ['datetime', '15Tf_rtn']]].copy()

            d.dropna(how='any', inplace=True)
            d.reset_index(drop=True, inplace=True)

            if len(d) < 100:
                comm_components[comm] = []
                print(comm)
                continue
            pca = decomposition.PCA()
            try:
                pca.fit(d)
            except Exception as e:
                print(e)
                print(comm, 'PASS in PCA')
                continue

            comm_components[comm] = [list(i) for i in pca.components_[:10]]
            comm_components[comm] = pca.components_[:10]

        self.components = comm_components

    def form_comm_factor(self, use_days=90):
        comm_factor = {}
        for comm in self.open_comm:
            t_comm_d = self.comm_factor_data[comm].loc[
                (self.comm_factor_data[comm]['datetime'] < self.agent.earth_calender.now_date) &
                (self.comm_factor_data[comm]['datetime'] >=
                 (self.agent.earth_calender.now_date - timedelta(days=use_days)))
            ]
            comm_factor[comm] = t_comm_d.reset_index(drop=True)
        return comm_factor

    def update_use_factor_list_if_must(self):
        # 每30天更新一次
        if (self.agent.earth_calender.now_date - self.last_update_date)  > timedelta(days=7):
            # 使用过去90天的数据更新
            comm_factor = self.form_comm_factor(use_days=90)

            self.renew_pca_components(comm_factor=comm_factor)

            self.last_update_date = self.agent.earth_calender.now_date

    @timer
    def strategy_target_pos(self, now_dt):
        comm_factor = self.form_train_data(now_dt=now_dt, rough_data_len=1000)
        mp_data_set = []
        for comm in comm_factor.keys():
            if comm not in self.components.keys():
                continue
            t_comm_data = comm_factor[comm][-1-self.train_data_len:].copy().reset_index(drop=True)

            t_comm_data[[i for i in t_comm_data if i not in ['datetime', '15Tf_rtn']]] = \
                t_comm_data[[i for i in t_comm_data if i not in ['datetime', '15Tf_rtn']]].fillna(method='ffill')

            for i in range(len(self.components[comm])):
                c = t_comm_data[[
                    i for i in t_comm_data if (i not in ['datetime', '15Tf_rtn']) & (not i.startswith('trans'))
                ]].values.dot(self.components[comm][i].transpose())

                t_comm_data['trans_%s' % i] = pd.DataFrame(c)[0]

            t_comm_data = t_comm_data[['trans_%s' % i for i in range(len(self.components[comm]))] + ['15Tf_rtn']]

            train_data = t_comm_data[:-1]
            test_data = t_comm_data.iloc[-1]

            if len(train_data.columns) <= 1 :
                # print(comm, 'pass')
                continue
            else:
                mp_data_set.append(
                    {
                        'comm': comm,
                        'train_data': train_data,
                        'test_data': test_data
                    }
                )
        res_list = []

        for dataset in mp_data_set:
            try:
                res_list.append(self.mp_pred_rtn_RF(dataset['comm'], dataset['train_data'], dataset['test_data']))
            except Exception as e:
                print(dataset['comm'], 'PASS')
                print(e)
                continue

        _p_res = {'now_dt': pd.to_datetime(now_dt) - relativedelta(minutes=1)}
        for res in res_list:
            _p_res[res['comm']] = res['pred_res']

        self.signals.append(_p_res)

    def _termly_process(self, term_begin_time):
        """
        每期进行的流程
        :param term_begin_time:
        :return:
        """

        # 再开仓
        self.strategy_target_pos(
            now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time)
        )

    def _daily_process(self):
        self.open_comm = self._open_comm()
        self.update_use_factor_list_if_must()
        print(self.agent.earth_calender.now_date)

        for comm in self.exchange.contract_dict.keys():
            # 未上市的商品
            if self.exchange.contract_dict[comm].first_listed_date > self.agent.earth_calender.now_date:
                continue
            # 已经退市的商品
            if self.exchange.contract_dict[comm].last_de_listed_date < self.agent.earth_calender.now_date:
                continue
            print(comm)

            self.exchange.contract_dict[comm].renew_main_sec_contract(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[comm].renew_operate_contract(now_date=self.agent.earth_calender.now_date)

        # 逐期遍历
        for term_begin_time in self.term_list:
            self._termly_process(term_begin_time=term_begin_time)

        print('*' * 30)
        print('DATE', self.agent.earth_calender.now_date)
        print('*' * 30)
        print('=' * 50)

        if self.agent.earth_calender.now_date.strftime('%m') == '02':
            signal_df = pd.DataFrame(self.signals)
            signal_df.to_csv('%s_pca_signal_df.csv' % self.agent.earth_calender.now_date.strftime('%Y'))


if __name__ == '__main__':

    syn_test = PCADeCorrLongTermTest(
        factor_name='hf_syn',
        begin_date='2015-05-10',
        end_date='2021-02-28',
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] in ['PB', 'A']],
        contract_list=NORMAL_CONTRACT_INFO,
        local_factor_data_path=local_15t_factor_path,
        local_data_path=local_data_path,
        term='15T',
        leverage=True,
        train_data_len=100
    )
    syn_test.test()
