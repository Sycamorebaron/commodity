import sys
import os
import pandas as pd
from dateutil.relativedelta import relativedelta
import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import timedelta
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from factor.backtest.factor_test import BackTest
from utils.base_para import local_data_path, local_5t_factor_path, NORMAL_CONTRACT_INFO

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



class DoiRtnLongTerm(BackTest):
    def __init__(
            self, factor_name, begin_date, end_date, init_cash, contract_list, local_factor_data_path, local_data_path,
            term, leverage, train_data_len, night
    ):
        BackTest.__init__(
            self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path, term, leverage, night
        )
        self.doi_rtn_res = []

    def transform_data(self):
        for comm in self.exchange.contract_dict.keys():

            # 未上市的商品
            if self.exchange.contract_dict[comm].first_listed_date > self.agent.earth_calender.now_date:
                continue
            # 已经退市的商品
            if self.exchange.contract_dict[comm].last_de_listed_date < self.agent.earth_calender.now_date:
                continue

            op_contract = self.exchange.contract_dict[comm].operate_contract
            print(comm, op_contract)
            data = self.exchange.contract_dict[comm].data_dict[op_contract][[
                'datetime', 'open', 'close', 'open_interest'
            ]].copy()

            if data['datetime'].iloc[1] - data['datetime'].iloc[0] < timedelta(days=1):
                data['open_oi'] = data['open_interest']
                data['close_oi'] = data['open_interest']

                data = data.resample(on='datetime', rule='1D').agg(
                    {
                        'open': 'first',
                        'close': 'last',
                        'open_interest': 'last',
                        'open_oi': 'first',
                        'close_oi': 'last'
                    }
                )
                data['rtn'] = data['close'] / data['open'] - 1
                data['doi'] = data['close_oi'] / data['open_oi'] - 1
                data.reset_index(inplace=True)
                self.exchange.contract_dict[comm].data_dict[op_contract] = data


    def daily_data(self):
        daily_res = {'date': self.agent.earth_calender.now_date}
        for comm in self.exchange.contract_dict.keys():

            # 未上市的商品
            if self.exchange.contract_dict[comm].first_listed_date > self.agent.earth_calender.now_date:
                continue
            # 已经退市的商品
            if self.exchange.contract_dict[comm].last_de_listed_date < self.agent.earth_calender.now_date:
                continue

            op_contract = self.exchange.contract_dict[comm].operate_contract
            comm_d = self.exchange.contract_dict[comm].data_dict[op_contract]

            daily_res['%s_doi' % comm] = comm_d.loc[
                comm_d['datetime'] == self.agent.earth_calender.now_date, 'doi'
            ].values[0]
            daily_res['%s_rtn' % comm] = comm_d.loc[
                comm_d['datetime'] == self.agent.earth_calender.now_date, 'rtn'
            ].values[0]

        self.doi_rtn_res.append(daily_res)

    def _daily_process(self):
        """
        每日进行的流程
        :return:
        """
        print(self.agent.earth_calender.now_date)

        for comm in self.exchange.contract_dict.keys():
            # 未上市的商品
            if self.exchange.contract_dict[comm].first_listed_date > self.agent.earth_calender.now_date:
                continue
            # 已经退市的商品
            if self.exchange.contract_dict[comm].last_de_listed_date < self.agent.earth_calender.now_date:
                continue

            self.exchange.contract_dict[comm].renew_main_sec_contract(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[comm].renew_operate_contract(now_date=self.agent.earth_calender.now_date)
            print(comm, self.exchange.contract_dict[comm].operate_contract)
        self.transform_data()  # 数据切到1D

        self.daily_data()


        print('*' * 30)
        print('DATE', self.agent.earth_calender.now_date)
        print('EQUITY', self.exchange.account.equity)
        print('*' * 30)
        print('=' * 50)


class DoiRtnShortTerm(DoiRtnLongTerm):
    @timer
    def transform_data(self):
        for comm in self.exchange.contract_dict.keys():

            # 未上市的商品
            if self.exchange.contract_dict[comm].first_listed_date > self.agent.earth_calender.now_date:
                continue
            # 已经退市的商品
            if self.exchange.contract_dict[comm].last_de_listed_date < self.agent.earth_calender.now_date:
                continue

            op_contract = self.exchange.contract_dict[comm].operate_contract
            data = self.exchange.contract_dict[comm].data_dict[op_contract].copy()
            if 'rtn' not in data.columns:
                data['rtn'] = data['close'] / data['open'] - 1
                data['doi'] = data['open_interest'] / data['open_interest'].shift(1) - 1
                data['date'] = data['datetime'].apply(lambda x: x.strftime('%Y-%m-%d'))
                self.exchange.contract_dict[comm].data_dict[op_contract] = data
    @timer
    def daily_data(self):
        daily_res = {'date': self.agent.earth_calender.now_date}
        for comm in self.exchange.contract_dict.keys():

            # 未上市的商品
            if self.exchange.contract_dict[comm].first_listed_date > self.agent.earth_calender.now_date:
                continue
            # 已经退市的商品
            if self.exchange.contract_dict[comm].last_de_listed_date < self.agent.earth_calender.now_date:
                continue

            op_contract = self.exchange.contract_dict[comm].operate_contract
            comm_d = self.exchange.contract_dict[comm].data_dict[op_contract]
            comm_d_today = comm_d.loc[comm_d['date']  == self.agent.earth_calender.now_date.strftime('%Y-%m-%d')].copy()

            daily_res['%s_corr' % comm] = comm_d_today['rtn'].corr(comm_d_today['doi'])
            daily_res['%s_rtn' % comm] = comm_d_today['close'].iloc[-1] / comm_d_today['open'].iloc[0] - 1
        self.doi_rtn_res.append(daily_res)


def ts_corr(data, ts_len):
    data['corr'] = None
    for i in range(ts_len, len(data)):
        data['corr'].iloc[i] = data[i - ts_len: i]['rtn'].corr(data[i - ts_len: i]['doi'])
    return data


if __name__ == '__main__':
    """
    # doi rtn日频计算
    back_test = DoiRtnLongTerm(
        factor_name='moment',
        begin_date='2011-01-01',
        end_date='2021-01-31',
        init_cash=10000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] in ['SA', 'L', 'M', 'TC', 'JM']],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path,
        term='15T',
        leverage=True,
        night=True,
        train_data_len=100,
        local_factor_data_path=local_5t_factor_path
    )
    back_test.test()
    doi_rtn_df = pd.DataFrame(back_test.doi_rtn_res)
    doi_rtn_df.to_csv(r'D:\commodity\doirtn_study\data\doi_rtn.csv')
    print(doi_rtn_df)
    """

    """
    data = pd.read_csv(r'D:\commodity\doirtn_study\data\doi_rtn.csv')

    # 不同的时间长短下单品种的时间序列相关系数
    comm_list = list(set([i.split('_')[0] for i in data.columns if i.endswith('_rtn') or i.endswith('_doi')]))
    for comm in comm_list:
        comm_data = data[['date', '%s_doi' % comm, '%s_rtn' % comm]].copy()
        comm_data.columns = ['date', 'doi', 'rtn']
        for ts_len in range(100, 300, 50):
            res = ts_corr(data=comm_data.copy(), ts_len=ts_len)
            comm_data['%s_corr' % ts_len] = res['corr']

        comm_data = comm_data[['date', 'rtn'] + [i for i in comm_data.columns if i.endswith('corr')]]
        comm_data['price'] = (1 + comm_data['rtn']).cumprod()
        comm_data['0_corr'] = 0
        comm_data.set_index('date', inplace=True)
        print(comm_data)
        fig, ax = plt.subplots(figsize=[15, 8])
        ax.plot(comm_data[[i for i in comm_data.columns if i.endswith('_corr')]])
        ax2 = ax.twinx()
        ax2.plot(comm_data['price'], color='blue')
        tick_spacing = comm_data.index.size / 5
        ax.xaxis.set_major_locator(mticker.MultipleLocator(tick_spacing))
        plt.title(comm)
        plt.savefig(r'D:\commodity\doirtn_study\data\ts_corr_fig\%s.png' % comm)
        comm_data.to_csv(r'D:\commodity\doirtn_study\data\ts_corr_data\%s.csv' % comm)
    """


    """
    # doi rtn corr分钟频计算
    back_test = DoiRtnShortTerm(
        factor_name='moment',
        begin_date='2011-01-01',
        end_date='2021-01-31',
        init_cash=10000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] in ['SA', 'L', 'M', 'TC', 'JM']],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path,
        term='15T',
        leverage=True,
        night=True,
        train_data_len=100,
        local_factor_data_path=local_5t_factor_path
    )
    back_test.test()
    doi_rtn_df = pd.DataFrame(back_test.doi_rtn_res)
    doi_rtn_df.to_csv(r'D:\commodity\doirtn_study\data\HF_doi_rtn.csv')
    print(doi_rtn_df)

    """

    data = pd.read_csv(r'D:\commodity\doirtn_study\data\HF_doi_rtn.csv')
    print(data)
    comm_list = list(set([i.split('_')[0] for i in data.columns if i.endswith('_rtn') or i.endswith('_doi')]))
    for comm in comm_list:
        comm_data = data[['date', '%s_corr' % comm, '%s_rtn' % comm]].copy()
        comm_data.columns = ['date', 'corr', 'rtn']
        for ts_len in range(100, 300, 50):
            comm_data['%s_corr' % ts_len] = comm_data['corr'].rolling(ts_len).mean()
        comm_data['price'] = (1 + comm_data['rtn']).cumprod()
        comm_data.set_index('date', inplace=True)
        comm_data['0_corr'] = 0
        comm_data.to_csv(r'D:\commodity\doirtn_study\data\HF_ts_corr_data\%s.csv' % comm)
        fig, ax = plt.subplots(figsize=[15, 8])
        ax.plot(comm_data[[i for i in comm_data.columns if i.endswith('_corr')]])
        ax2 = ax.twinx()
        ax2.plot(comm_data['price'], color='blue')
        tick_spacing = comm_data.index.size / 5
        ax.xaxis.set_major_locator(mticker.MultipleLocator(tick_spacing))
        plt.title(comm)
        plt.legend(range(100, 300, 50))
        plt.savefig(r'D:\commodity\doirtn_study\data\HF_ts_corr_fig\%s.png' % comm)
