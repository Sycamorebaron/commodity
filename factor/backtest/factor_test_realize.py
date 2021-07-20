import sys
import os
from datetime import timedelta

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from factor.test.main_test import MainTest
from utils.base_para import *


class BackTest(MainTest):
    def __init__(self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path, term, leverage, night):
        MainTest.__init__(self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path, leverage)
        self.term = term
        self.term_list = self._gen_term_list(term=term, night=night)

    def _last_dt(self, now_dt):
        """
        找到用于计算因子的数据开始时间
        :param now_dt:
        :return:
        """
        if pd.to_datetime(now_dt).strftime('%H:%M') != '09:01':
            return '%s %s:00' % (
                pd.to_datetime(now_dt).strftime('%Y-%m-%d'),
                self.term_list[self.term_list.index(pd.to_datetime(now_dt).strftime('%H:%M')) - 1]
            )
        else:
            return '%s %s:00' % (
                (self.exchange.trade_calender.get_last_trading_date(
                    date=self.agent.earth_calender.now_date
                )).strftime('%Y-%m-%d'),
                self.term_list[-1]
            )

    def _get_cal_factor_data(self, comm, now_dt, last_dt):
        """
        找到用于计算因子的数据
        :param comm:
        :param now_dt:
        :param last_dt:
        :return:
        """

        now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
        cond1 = data['datetime'] >= last_dt
        cond2 = data['datetime'] < now_dt
        cal_factor_data = data.loc[cond1 & cond2].reset_index(drop=True)

        return cal_factor_data

    @staticmethod
    def _gen_term_list(term, night):
        if not night:
            begin_time = pd.to_datetime('2000-01-01 09:01')
            end_time = pd.to_datetime('2000-01-01 15:00')
            rest_time_begin_1 = pd.to_datetime('2000-01-01 10:15')
            rest_time_end_1 = pd.to_datetime('2000-01-01 10:30')
            rest_time_begin_2 = pd.to_datetime('2000-01-01 11:30')
            rest_time_end_2 = pd.to_datetime('2000-01-01 13:30')

            now_term_begin = begin_time
            term_list = []
            if term.endswith('T'):
                while now_term_begin < end_time:
                    if (now_term_begin < rest_time_begin_1) or \
                        ((now_term_begin > rest_time_end_1) & (now_term_begin < rest_time_begin_2)) or \
                        (now_term_begin > rest_time_end_2):
                        term_list.append(now_term_begin.strftime('%H:%M'))
                    now_term_begin += timedelta(minutes=int(term.strip('T')))
            elif term.endswith('H'):
                while now_term_begin < end_time:
                    if (now_term_begin < rest_time_begin_1) or \
                        ((now_term_begin > rest_time_end_1) & (now_term_begin < rest_time_begin_2)) or \
                        (now_term_begin > rest_time_end_2):
                        term_list.append(now_term_begin.strftime('%H:%M'))
                    now_term_begin += timedelta(hours=int(term.strip('H')))
            else:
                raise Exception('TERM NOT SUPPORT')
        else:

            begin_time = pd.to_datetime('2000-01-01 09:01')
            end_time = pd.to_datetime('2000-01-01 23:00')
            rest_time_begin_1 = pd.to_datetime('2000-01-01 10:15')
            rest_time_end_1 = pd.to_datetime('2000-01-01 10:30')

            rest_time_begin_2 = pd.to_datetime('2000-01-01 11:30')
            rest_time_end_2 = pd.to_datetime('2000-01-01 13:30')

            rest_time_begin_3 = pd.to_datetime('2000-01-01 15:00')
            rest_time_end_3 = pd.to_datetime('2000-01-01 21:00')

            now_term_begin = begin_time
            term_list = []
            if term.endswith('T'):
                while now_term_begin < end_time:
                    if (now_term_begin < rest_time_begin_1) or \
                            ((now_term_begin > rest_time_end_1) & (now_term_begin < rest_time_begin_2)) or \
                            (now_term_begin > rest_time_end_2) & (now_term_begin < rest_time_begin_3) or \
                            (now_term_begin > rest_time_end_3):
                        term_list.append(now_term_begin.strftime('%H:%M'))
                    now_term_begin += timedelta(minutes=int(term.strip('T')))
            elif term.endswith('H'):
                while now_term_begin < end_time:
                    if (now_term_begin < rest_time_begin_1) or \
                            ((now_term_begin > rest_time_end_1) & (now_term_begin < rest_time_begin_2)) or \
                            (now_term_begin > rest_time_end_2) & (now_term_begin < rest_time_begin_3) or \
                            (now_term_begin > rest_time_end_3):
                        term_list.append(now_term_begin.strftime('%H:%M'))
                    now_term_begin += timedelta(hours=int(term.strip('H')))

        return term_list

    def clear_position(self, term_begin_time):
        close_pos = {}
        for comm in self.exchange.account.position.holding_position.keys():
            for contract in self.exchange.account.position.holding_position[comm].keys():
                close_pos[contract] = 0
        if len(close_pos):
            close_trade_info = self.agent.change_position(
                exchange=self.exchange,
                target_pos=close_pos,
                now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time)
            )
            self.exchange.account.equity = self.exchange.account.cash
            self.agent.recorder.record_trade(info=close_trade_info)

    def strategy_target_pos(self, now_dt):
        """
        target pos中要包含现有持仓平仓的 position
        target_pos = {'L2005': 0.5, 'FG2005': -0.5}
        :param now_dt:
        :return:
        """
        return {'L2005': 0.5, 'FG2005': -0.5}

    def _termly_process(self, term_begin_time):
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

            close_trade_info = self.agent.change_position(
                exchange=self.exchange,
                target_pos=close_pos,
                now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time),
                field='close'
            )
            self.exchange.account.equity = self.exchange.account.cash
            # self.agent.recorder.record_trade(info=close_trade_info)

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
        # self.agent.recorder.record_trade(info=open_trade_info)


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
            last_end_time = pd.to_datetime(self._last_dt(now_dt=term_begin_time)) + timedelta(minutes=int(self.term[:-1]) - 1)

            close_trade_info = self.agent.change_position(
                exchange=self.exchange,
                target_pos=close_pos,
                now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time),
                field='close',
            )
            self.exchange.account.equity = self.exchange.account.cash
            self.agent.recorder.record_trade(info=close_trade_info)

        # if term_begin_time not in ['10:01', '10:31']:
        # if term_begin_time not in ['09:01', '09:16', '10:01', '10:16', '10:31', '13:01', '21:01']:
        if term_begin_time not in ['09:01', '10:16', '13:31', '21:01']:

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
            print(comm)

            self.exchange.contract_dict[comm].renew_main_sec_contract(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[comm].renew_operate_contract(now_date=self.agent.earth_calender.now_date)

        # 逐期遍历
        for term_begin_time in self.term_list:
            self._termly_process(term_begin_time=term_begin_time)

        # 每日清仓，只需要平仓手上的仓位
        self.clear_position(term_begin_time=self.term_list[-1])

        # 记录资金情况
        self.agent.recorder.record_equity(
            info={
                'date': self.agent.earth_calender.now_date,
                'equity': self.exchange.account.equity,
            }
        )

        print('*' * 30)
        print('DATE', self.agent.earth_calender.now_date)
        print('EQUITY', self.exchange.account.equity)
        print('*' * 30)
        print('=' * 50)


class VARIMABackTest(BackTest):
    def __init__(self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path, term, leverage, night):
        BackTest.__init__(self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path, term, leverage, night)
        self.hist_rtn = {}

    def _get_cal_factor_data(self, comm, now_dt, last_dt):
        op_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        d = self.exchange.contract_dict[comm].data_dict[op_contract].copy()
        d = d.loc[d['datetime'] < now_dt][-15:].reset_index(drop=True)
        rtn = d['close'].iloc[-1] / d['open'].iloc[0] - 1
        if comm in self.hist_rtn.keys():
            self.hist_rtn[comm].append(
                {
                    'candle_begin_time': d['datetime'].iloc[0] - timedelta(minutes=1),
                    'contract': op_contract,
                    'rtn': rtn,
                    'abs_rtn': abs(rtn)
                }
            )
        else:
            self.hist_rtn[comm] = [
                {
                    'candle_begin_time': d['datetime'].iloc[0] - timedelta(minutes=1),
                    'contract': op_contract,
                    'rtn': rtn,
                    'abs_rtn': abs(rtn)
                }
            ]

    def strategy_target_pos(self, now_dt):
        use_data_len = 300
        for comm in self.exchange.contract_dict.keys():
            if (pd.to_datetime(now_dt) < self.exchange.contract_dict[comm].first_listed_date + timedelta(days=2)) or \
                    (pd.to_datetime(now_dt) > self.exchange.contract_dict[comm].last_de_listed_date):
                continue

            self._get_cal_factor_data(
                comm=comm, now_dt=now_dt, last_dt=self._last_dt(now_dt=now_dt)
            )

        sum_comm_data = pd.DataFrame()
        for comm in self.hist_rtn.keys():
            if len(self.hist_rtn[comm]) < use_data_len + 1:
                continue
            comm_df = pd.DataFrame(self.hist_rtn[comm])
            # comm_df['f_rtn'] = comm_df['rtn'].shift(-1)

            comm_df = comm_df[['candle_begin_time', 'rtn']]
            print(comm_df)
            comm_df.columns = ['candle_begin_time', self.hist_rtn[comm][-1]['contract']]
            if len(sum_comm_data):
                sum_comm_data = sum_comm_data.merge(comm_df, on='candle_begin_time', how='outer')
            else:
                sum_comm_data = comm_df

        if len(sum_comm_data):
            print(sum_comm_data)
            sum_comm_data.to_csv(r'C:\Users\sycam\Desktop\testdata.csv')
            exit()

        signal_pos = {}

        # 有信号的均分仓位
        if len(signal_pos):
            for k in signal_pos.keys():
                signal_pos[k] /= len(signal_pos)

        return signal_pos

    def _termly_process(self, term_begin_time):
        BackTest._termly_process_skip_rest(self, term_begin_time)
        print('cumulated fee', self.agent.trade_center.cumulated_fee)


if __name__ == '__main__':
    back_test = VARIMABackTest(
        test_name='moment',
        begin_date='2014-01-01',
        end_date='2020-12-31',
        init_cash=10000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] == 'FG'],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path,
        term='15T',
        leverage=False,
        night=False
    )
    back_test.test()
    back_test.agent.recorder.equity_curve().to_csv(r'C:\Users\sycam\Desktop\corr_reverse.csv')
    back_test.agent.recorder.trade_hist().to_csv(r'C:\Users\sycam\Desktop\corr_reverse_trade_hist.csv')
    # back_test.agent.recorder.trade_hist().to_csv(r'C:\Users\sycam\Desktop\momentum.csv')
