import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from factor.test.main_test import MainTest
from utils.base_para import *


class BackTest(MainTest):
    def __init__(self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        MainTest.__init__(self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path)

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

        # 根据策略计算目标仓位
        print(self.exchange.contract_dict['L'].operate_contract)
        print(self.exchange.contract_dict['FG'].operate_contract)


        target_pos = {'L2005': 0.5, 'FG2005': -0.5}

        # 根据目标仓位调仓
        trade_info = self.agent.change_position(
            exchange=self.exchange,
            target_pos=target_pos,
            now_dt='2020-01-02 09:01:00'
        )
        print(trade_info)
        exit()

        # 记录交易
        self.agent.recorder.record_trade(info=trade_info)

        # 每日结算
        self.exchange.account.daily_settlement(
            now_date=self.agent.earth_calender.now_date,
            contract_dict=self.exchange.contract_dict
        )

        # 记录资金情况
        self.agent.recorder.record_equity(
            info={
                'date': self.agent.earth_calender.now_date,
                'target_pos': target_pos,
                'position': self.exchange.account.position.holding_position,
                'cash': self.exchange.account.cash,
                'equity': self.exchange.account.equity,
                'risk_rate': self.exchange.account.risk_rate
            }
        )

        print('*' * 30)
        print('DATE', self.agent.earth_calender.now_date)
        print('POSITION', self.exchange.account.position.holding_position)
        print('CASH', self.exchange.account.cash)
        print('EQUITY', self.exchange.account.equity)
        print('RISK RATE', self.exchange.account.risk_rate)
        print('*' * 30)
        print('=' * 50)


if __name__ == '__main__':
    back_test = BackTest(
        test_name='moment',
        begin_date='2020-01-01',
        end_date='2021-02-28',
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO[:10],
        local_data_path=local_data_path
    )
    back_test.test()
