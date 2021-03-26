from factor.test.main_test import MainTest
from utils.base_para import *

class FactorTest(MainTest):
    def _daily_process(self):
        print(self.agent.earth_calender.now_date)
        print(self.exchange.trade_calender.is_trade_date)
        pass


if __name__ == '__main__':
    factor_test = FactorTest(
        test_name='factor_test',
        begin_date='2010-01-01',
        end_date='2020-12-31',
        init_cash=10000000,
        contract_list=FULL_CONTRACT_INFO
    )

    factor_test.test()