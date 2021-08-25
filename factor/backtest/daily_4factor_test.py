import sys
import os
from datetime import timedelta

import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from factor.backtest.factor_test_realize import BackTest
from utils.base_para import *


class FourFactorTest(BackTest):
    def __init__(self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path, term, leverage, night, comm):
        BackTest.__init__(self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path, term, leverage, night, comm)
        self.hist_factor = {}

    def _get_cal_factor_data(self, comm, now_dt, last_dt):
        op_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        d = self.exchange.contract_dict[comm].data_dict[op_contract].copy()
        d = d.loc[d['datetime'] < last_dt][-15:].reset_index(drop=True)  # 此处使用前一日的数据
        d['rtn'] = d['close'] / d['open'] - 1
        d['dv'] = d['volume'] - d['volume'].shift(1)

        if comm in self.hist_factor.keys():
            self.hist_factor[comm].append(
                {
                    'candle_begin_time': d['datetime'].iloc[0] - timedelta(minutes=1),
                    'contract': op_contract,
                    'price': d['high'].max(),  # 价格因子
                    'pv': d['close'].shift(1).corr(d['volume']),  # 量价相关性因子
                    'rdv': d['rtn'].shift(2).corr(d['dv']),  # 收益率、成交量变化相关性
                    'kurt': d['rtn'].kurtosis(),  # 偏度因子
                }
            )
        else:
            self.hist_factor[comm] = [
                {
                    'candle_begin_time': d['datetime'].iloc[0] - timedelta(minutes=1),
                    'contract': op_contract,
                    'price': d['high'].max(),  # 价格因子
                    'pv': d['close'].shift(1).corr(d['volume']),  # 量价相关性因子
                    'rdv': d['rtn'].shift(2).corr(d['dv']),  # 收益率 成交量变化相关性
                    'kurt': d['rtn'].kurtosis(),  # 偏度因子
                }
            ]

    def strategy_target_pos(self, now_dt):

        signal_pos = {}
        hist_data_len = 100

        for comm in self.exchange.contract_dict.keys():
            if (pd.to_datetime(now_dt) < self.exchange.contract_dict[comm].first_listed_date + timedelta(days=2)) or \
                    (pd.to_datetime(now_dt) > self.exchange.contract_dict[comm].last_de_listed_date):
                continue

            self._get_cal_factor_data(
                comm=comm, now_dt=now_dt, last_dt=self._last_dt(now_dt=now_dt)
            )

            if len(self.hist_factor[comm]) < hist_data_len + 1:
                continue

            op_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )

            signal_pos[op_contract] = 0

            factor_data = pd.DataFrame(self.hist_factor[comm])[-100:].reset_index(drop=True)
            for factor in ['price', 'pv', 'rdv', 'kurt']:
                if factor_data[factor].iloc[-1] < factor_data[factor].quantile(0.05):
                    signal_pos[op_contract] -= 1
                elif factor_data[factor].iloc[-1] > factor_data[factor].quantile(0.95):
                    signal_pos[op_contract] += 1

        # 有信号的均分仓位
        if len(signal_pos):
            sum_pos = sum([abs(signal_pos[i]) for i in signal_pos.keys()])
            if sum_pos != 0:
                for k in signal_pos.keys():
                    signal_pos[k] /= sum_pos

        return signal_pos

    def _termly_process(self, term_begin_time):

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
        print('cumulated fee', self.agent.trade_center.cumulated_fee)

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

            if term_begin_time == '09:01':
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


if __name__ == '__main__':
    back_test = FourFactorTest(
        test_name='FourFactorTest',
        begin_date='2012-01-01',
        end_date='2020-12-31',
        init_cash=10000000,
        contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] not in [
            'FG', 'CJ', 'PB', 'C', 'EG', 'ZC', 'ZN', 'UR', 'LU', 'L', 'AU', 'BC', 'LH', 'PF', 'PK'
        ]],
        # contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path,
        term='15T',
        leverage=False,
        night=False,
        comm=0.000
    )
    back_test.test()

    back_test.agent.recorder.equity_curve().to_csv(
        os.path.join(OUTPUT_DATA_PATH, 'FILTERED_%s_equity_curve.csv' % back_test.test_name)
    )
    back_test.agent.recorder.trade_hist().to_csv(
        os.path.join(OUTPUT_DATA_PATH, 'FILTERED_%s_trade_hist.csv' % back_test.test_name)
    )
