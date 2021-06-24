import sys
import os
import pandas as pd
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
# pd.set_option('display.max_rows', 200)


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
        self.last_update_date = pd.DataFrame('2000-01-01')

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
            print(comm_factor)
            exit()


    def update_use_factor_list_if_must(self):
        # 每30天更新一次
        if self.agent.earth_calender.now_date - self.use_factor_list  > timedelta(days=30):
            # 使用过去90天的数据更新
            comm_factor = self.form_comm_factor(use_days=90)

            self.last_update_date = self.agent.earth_calender.now_date
        self.use_factor_list = []


    def _daily_process(self):

        HFSynTest._daily_process(self)
        self.update_use_factor_list_if_must()


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


if __name__ == '__main__':

    syn_test = LongTermTest(
        factor_name='hf_syn',
        begin_date='2015-02-01',
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
