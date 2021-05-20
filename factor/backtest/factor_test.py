import sys
import os
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from factor.test.main_test import MainTest
from utils.base_para import *


class BackTest(MainTest):
    def __init__(self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path, term):
        MainTest.__init__(self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.term_list = self._gen_term_list(term)


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
        data = self.exchange.contract_dict[comm].data_dict[
            self.exchange.contract_dict[comm].operate_contract
        ]
        cond1 = data['datetime'] >= last_dt
        cond2 = data['datetime'] < now_dt
        cal_factor_data = data.loc[cond1 & cond2].reset_index(drop=True)

        return cal_factor_data

    @staticmethod
    def _gen_term_list(term):
        begin_time = pd.to_datetime('2000-01-01 09:01')
        end_time = pd.to_datetime('2000-01-01 15:00')
        rest_time_begin = pd.to_datetime('2000-01-01 11:30')
        rest_time_end = pd.to_datetime('2000-01-01 13:30')

        now_term_begin = begin_time
        term_list = []
        if term.endswith('T'):
            while now_term_begin < end_time:
                if (now_term_begin < rest_time_begin) or (now_term_begin > rest_time_end):
                    term_list.append(now_term_begin.strftime('%H:%M'))
                now_term_begin += timedelta(minutes=int(term.strip('T')))
        elif term.endswith('H'):
            while now_term_begin < end_time:
                if (now_term_begin < rest_time_begin) or (now_term_begin > rest_time_end):
                    term_list.append(now_term_begin.strftime('%H:%M'))
                now_term_begin += timedelta(hours=int(term.strip('H')))
        else:
            raise Exception('TERM NOT SUPPORT')

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
                now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time)
            )
            self.exchange.account.equity = self.exchange.account.cash
            self.agent.recorder.record_trade(info=close_trade_info)

        # 再开仓
        target_pos = self.strategy_target_pos(
            now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time)
        )
        # print('target_pos', target_pos)

        # 根据目标仓位调仓
        open_trade_info = self.agent.change_position(
            exchange=self.exchange,
            target_pos=target_pos,
            now_dt='%s %s:00' % (self.agent.earth_calender.now_date.strftime('%Y-%m-%d'), term_begin_time)
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



class MomentumBackTest(BackTest):
    def strategy_target_pos(self, now_dt):

        contract_factor_list = []
        for comm in self.exchange.contract_dict.keys():
            if (pd.to_datetime(now_dt) < self.exchange.contract_dict[comm].first_listed_date) or \
                (pd.to_datetime(now_dt) > self.exchange.contract_dict[comm].last_de_listed_date):
                continue
            cal_factor_data = self._get_cal_factor_data(
                comm=comm, now_dt=now_dt, last_dt=self._last_dt(now_dt=now_dt)
            )
            contract_factor_list.append(
                {
                    'contract': cal_factor_data['order_book_id'].iloc[0],
                    'factor': cal_factor_data['close'].iloc[-1] / cal_factor_data['open'].iloc[0] - 1
                }
            )
        contract_factor_df = \
            pd.DataFrame(contract_factor_list).sort_values(by='factor', ascending=False).reset_index(drop=True)

        signal_pos = {}

        # 已经弃用，在外部平仓
        # # 有持仓的合约仓位为0的平仓信号，否则trade中不会平仓！
        # # 而且要先平仓信号
        # for comm in self.exchange.account.position.holding_position.keys():
        #     for contract in self.exchange.account.position.holding_position[comm].keys():
        #         # 有持仓，且不在signal中
        #         if (self.exchange.account.position.holding_position[comm] != {}) & (contract not in signal_pos.keys()):
        #             signal_pos[contract] = 0

        # 开仓信号
        signal_pos[contract_factor_df['contract'].iloc[0]] = 0.5
        signal_pos[contract_factor_df['contract'].iloc[-1]] = -0.5

        return signal_pos



if __name__ == '__main__':
    back_test = MomentumBackTest(
        test_name='moment',
        begin_date='2011-01-01',
        end_date='2021-02-28',
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path,
        term='30T'
    )
    back_test.test()
