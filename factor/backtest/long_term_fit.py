import sys
import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from dateutil.relativedelta import relativedelta
import numpy as np
from multiprocessing import Pool
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

    def _t_factor_list(self, comm_factor):
        return self.use_factor_list


    def update_use_factor_list(self):
        self.use_factor_list = []

    def _daily_process(self):

        HFSynTest._daily_process(self)
        self.update_use_factor_list()





    def _termly_process_skip_rest(self, term_begin_time):
        """
        每期进行的流程
        :param term_begin_time:
        :return:
        """
        # print('$' * 25, term_begin_time, '$' * 25)
        # print('-' * 25, 'before change position', '-' * 25)
        # print('CASH', self.exchange.account.cash)
        # print('position\n', self.exchange.account.position.holding_position)
        # print('-' * 70)

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

        # if term_begin_time not in ['10:01', '10:31']:
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

            # 记录交易
            self.agent.recorder.record_trade(info=open_trade_info)
            # print('-' * 25, 'after change position', '-' * 25)
            # print('CASH', self.exchange.account.cash)
            # print('position\n',self.exchange.account.position.holding_position)
            # print('-' * 70)
            # print('$' * 55)
