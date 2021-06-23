import sys
import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from dateutil.relativedelta import relativedelta
import numpy as np
from multiprocessing import Pool
import time
import xgboost as xgb
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from factor.backtest.factor_test import BackTest
from utils.base_para import local_data_path, local_15t_factor_path, NORMAL_CONTRACT_INFO

pd.set_option('expand_frame_repr', False)
# pd.set_option('display.max_rows', 200)


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, 'Timer', round(end-start, 4))
        return res
    return wrapper


class HFSynTest(BackTest):
    def __init__(
            self, factor_name, begin_date, end_date, init_cash, contract_list, local_factor_data_path, local_data_path,
            term, leverage, train_data_len
    ):
        BackTest.__init__(
            self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path, term, leverage, night=False
        )
        self.factor = self._load_factor(local_factor_data_path)
        self.comm_factor_data = self.form_factor_data()  # 保存按照商品保存的因子值
        self.open_comm = []
        self.train_data_len = train_data_len
        self.factor_ic = {}  # 计算后保存，防止重复运算

    @staticmethod
    def add_label(data):
        data['label'] = data['datetime'].apply(
            # lambda x: x - relativedelta(minutes=1) if (x.strftime('%M') in ['01', '31']) else None
            lambda x: x - relativedelta(minutes=1) if (x.strftime('%M') in ['01', '16', '31', '46']) else None
        )
        data['label'].fillna(method='ffill', inplace=True)
        return data

    @staticmethod
    def _cal_ic(t_data):
        """
        根据传入的t_data计算因子该期的ic
        :param t_data:
        :return:
        """
        _factor_df = t_data.loc[t_data['index'].apply(lambda x: not x.endswith('f_rtn'))].copy()
        _f_rtn_df = t_data.loc[t_data['index'].apply(lambda x: x.endswith('f_rtn'))].copy()
        _f_rtn_df['index'] = _f_rtn_df['index'].apply(lambda x: x.split('_')[0])
        _f_rtn_df.columns = ['comm', 'f_rtn']
        _factor_df.columns = ['comm', 'factor']
        t_factor_df = _f_rtn_df.merge(_factor_df, on='comm', how='inner')
        t_factor_df['f_rtn'] = t_factor_df['f_rtn'].astype(float)
        t_factor_df['factor'] = t_factor_df['factor'].astype(float)
        ic = t_factor_df['f_rtn'].corr(t_factor_df['factor'])
        return ic

    @staticmethod
    def pred_rtn(train_data, test_data):
        factors = [i for i in train_data.columns if i != '15Tf_rtn']
        train_X = train_data[factors]
        train_Y = train_data['15Tf_rtn']

        model_st = RandomForestRegressor(random_state=666)
        model_st.fit(X=train_X, y=train_Y)
        pred_res = model_st.predict(X=[list(test_data[factors])])[0]
        return pred_res

    @staticmethod
    def mp_pred_rtn_RF(comm, train_data, test_data):
        factors = [i for i in train_data.columns if i != '15Tf_rtn']
        train_X = train_data[factors]
        train_Y = train_data['15Tf_rtn']
        model_st = RandomForestRegressor(random_state=666, max_features = 'sqrt')
        model_st.fit(X=train_X, y=train_Y)

        pred_res = model_st.predict(X=[list(test_data[factors])])
        pred_res = pred_res[0]

        return {'comm': comm, 'pred_res': pred_res}

    def mp_pred_rtn_xgboost(self, comm, train_data, test_data):
        factors = [i for i in train_data.columns if i != '15Tf_rtn']
        train_X = train_data[factors].reset_index(drop=True)
        train_Y = train_data['15Tf_rtn'].reset_index(drop=True)
        model = xgb.XGBRegressor(n_estimators=7, objective='reg:squarederror')

        model.fit(X=train_X, y=train_Y)
        pred_res = model.predict(X=pd.DataFrame(test_data[factors]).T.reset_index(drop=True))

        pred_res = pred_res[0]

        return {'comm': comm, 'pred_res': pred_res}


    def _open_comm(self):
        """
        当前开放的合约
        :return:
        """
        return [
            i for i in self.exchange.contract_dict.keys() if
            self.exchange.contract_dict[i].first_listed_date <
            self.agent.earth_calender.now_date - relativedelta(days=self.train_data_len)
        ]

    @staticmethod
    def _load_factor(local_factor_data_path) -> dict:
        files = []
        factor_dict = {}
        for roots, dirs, files in os.walk(local_factor_data_path):
            if files:
                break
        print('load factors...')
        for f in files:
            print(f)
            data = pd.read_csv(os.path.join(local_factor_data_path, f))
            data['datetime'] = pd.to_datetime(data['datetime'])
            factor_dict[f.split('.')[0]] = data
        return factor_dict

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
            comm_factor[comm] = _comm_d

        return comm_factor

    def form_train_data(self, now_dt) -> dict:
        """
        筛选时间
        去掉夜盘：小时大于21 & 小时小于8
        去掉休息时间：10：15-10：30

        :param now_dt:
        :return:
        """
        comm_factor = {}
        for comm in self.open_comm:
            # _comm_d = pd.DataFrame()
            # for factor in self.factor.keys():
            #     print(comm, factor)
            #     _comm_f = self.factor[factor].loc[self.factor[factor]['datetime'] <= now_dt, ['datetime', comm]]
            #     _comm_f.columns = ['datetime', factor]
            #     _comm_f = _comm_f[-300:].reset_index(drop=True)
            #     if len(_comm_d):
            #         _comm_d = _comm_d.merge(_comm_f, on='datetime', how='outer')
            #     else:
            #         _comm_d = _comm_f
            #
            # _comm_d.sort_values(by='datetime', ascending=True, inplace=True)
            # cond1 = _comm_d['datetime'].dt.hour >= 9
            # cond2 = _comm_d['datetime'].dt.hour <= 15
            # _comm_d = _comm_d.loc[cond1 & cond2]
            #
            # _comm_d.reset_index(drop=True, inplace=True)
            # _comm_d['15Tf_rtn'] = _comm_d['15Thf_rtn'].shift(-1)
            #
            # print(_comm_d)
            # ============================================= 截取 =======================================================

            t_comm_d = self.comm_factor_data[comm].loc[self.comm_factor_data[comm]['datetime'] <= now_dt]
            t_comm_d = t_comm_d[-300:].reset_index(drop=True)
            # print(comm, 'form train data')
            # print(t_comm_d)
            # =========================================================================================================
            comm_factor[comm] = t_comm_d

        return comm_factor

    # @timer
    def _factor_exp_ic_dist(self, factor, factor_df):
        """
        计算因子的累计IC距离
        累计IC到0轴的面积/45度线到0轴的面积，越高说明越好
        :param factor_df:
        :return:
        """
        factor_ic = []
        for i in range(len(factor_df)):
            dt = factor_df['datetime'].iloc[i]
            if dt in self.factor_ic:
                if factor in self.factor_ic[dt].keys():
                    # 有时间、有因子，直接用
                    factor_ic.append(
                        {
                            'datetime': dt,
                            'ic': self.factor_ic[dt][factor]
                        }
                    )
                else:
                    # 有时间、无因子，计算因子
                    t_data = pd.DataFrame(factor_df.iloc[i]).reset_index()
                    t_data = t_data.dropna(subset=[i])[1:].reset_index(drop=True)
                    ic = self._cal_ic(t_data=t_data)
                    self.factor_ic[dt][factor] = ic
                    factor_ic.append(
                        {
                            'datetime': dt,
                            'ic': self.factor_ic[dt][factor]
                        }
                    )
            else:
                # 无时间，计算因子
                self.factor_ic[dt] = {}
                t_data = pd.DataFrame(factor_df.iloc[i]).reset_index()
                t_data = t_data.dropna(subset=[i])[1:].reset_index(drop=True)
                ic = self._cal_ic(t_data=t_data)
                self.factor_ic[dt][factor] = ic
                factor_ic.append(
                    {
                        'datetime': dt,
                        'ic': self.factor_ic[dt][factor]
                    }
                )

        factor_ic_df = pd.DataFrame(factor_ic)
        factor_ic_df['exp_ic'] = factor_ic_df['ic'].expanding().sum()
        exp_ic_dist = abs(factor_ic_df['exp_ic'].sum()) / sum(factor_ic_df.index)
        return exp_ic_dist

    def _t_factor_list(self, comm_factor):
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
            # train_data = t_comm_data[:-1]
            test_data = t_comm_data.iloc[-1]

            # print('train_data', comm, train_data)
            # print('test_data', comm, test_data)
            # test data 中有因子缺失，需要在训练数据中也将这部分因子去掉
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

                # pred_res = self.pred_rtn(train_data=train_data, test_data=test_data)
                # res_list.append(
                #     {
                #         'comm': comm,
                #         'pred_res': pred_res
                #     }
                # )

        # =========================================== MULTI PROCESS TEST ===============================================
        #         print('__train_data', comm, train_data)

                mp_data_set.append(
                    {
                        'comm': comm,
                        'train_data': train_data,
                        'test_data': test_data
                    }
                )
        pool = Pool(processes=4)
        jobs = []
        for dataset in mp_data_set:

            jobs.append(pool.apply_async(
                self.mp_pred_rtn_RF, (dataset['comm'], dataset['train_data'], dataset['test_data']))
            )
        pool.close()
        pool.join()
        res_list = [j.get() for j in jobs]
        # ==============================================================================================================
        # print(res_list)

        res_df = pd.DataFrame(res_list).sort_values(by='pred_res')
        signal = {
            self.exchange.contract_dict[res_df['comm'].iloc[0]].now_main_contract(
                now_date=self.agent.earth_calender.now_date): -0.5,
            self.exchange.contract_dict[res_df['comm'].iloc[-1]].now_main_contract(
                now_date=self.agent.earth_calender.now_date): 0.5
        }
        print(now_dt, signal)
        return signal

    def _daily_process(self):
        self.open_comm = self._open_comm()
        BackTest._daily_process(self)

        if self.agent.earth_calender.now_date.strftime('%m') == '12':

            eq_df = syn_test.agent.recorder.equity_curve()
            eq_df.to_csv('%s_syn_eq.csv' % self.agent.earth_calender.now_date.strftime('%Y'))


class PureSignal(HFSynTest):

    def __init__(
        self, factor_name, begin_date, end_date, init_cash, contract_list, local_factor_data_path, local_data_path,
        term, leverage, train_data_len
    ):
        HFSynTest.__init__(
            self, factor_name, begin_date, end_date, init_cash, contract_list, local_factor_data_path, local_data_path,
            term, leverage, train_data_len
        )
        self.signals = []

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
            # train_data = t_comm_data[:-1]
            test_data = t_comm_data.iloc[-1]

            # test data 中有因子缺失，需要在训练数据中也将这部分因子去掉
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
        pool = Pool(processes=8)
        jobs = []
        for dataset in mp_data_set:
            self.mp_pred_rtn_xgboost(dataset['comm'], dataset['train_data'], dataset['test_data'])
            exit()
            if len(dataset['train_data']) != 0:
                jobs.append(pool.apply_async(
                    self.mp_pred_rtn_xgboost, (dataset['comm'], dataset['train_data'], dataset['test_data']))
                )

        pool.close()
        pool.join()
        res_list = [j.get() for j in jobs]

        _p_res = {'now_dt': pd.to_datetime(now_dt) - relativedelta(minutes=1)}
        for res in res_list:
            _p_res[res['comm']] = res['pred_res']

        self.signals.append(_p_res)

    def _daily_process(self):
        self.open_comm = self._open_comm()

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
        print('EQUITY', self.exchange.account.equity)
        print('*' * 30)
        print('=' * 50)

        if self.agent.earth_calender.now_date.strftime('%m') == '02':
            signal_df = pd.DataFrame(self.signals)
            signal_df.to_csv('%s_signal_df.csv' % self.agent.earth_calender.now_date.strftime('%Y'))

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


if __name__ == '__main__':

    syn_test = PureSignal(
        factor_name='hf_syn',
        begin_date='2011-02-01',
        end_date='2021-02-28',
        init_cash=1000000,
        contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] in ['PB', 'L', 'C', 'M', 'RU', 'SR', 'A']],
        # contract_list=NORMAL_CONTRACT_INFO,
        local_factor_data_path=local_15t_factor_path,
        local_data_path=local_data_path,
        term='15T',
        leverage=False,
        train_data_len=100
    )
    syn_test.test()
    t_eq_df = syn_test.agent.recorder.equity_curve()
    t_eq_df.to_csv('syn_test_equity.csv')
