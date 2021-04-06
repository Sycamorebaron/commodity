from factor.test.main_test import MainTest
from utils.base_para import *
import pandas as pd

pd.set_option('expand_frame_repr', False)


class CalFactor(MainTest):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list):
        MainTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list)
        self.factor = []
        self.factor_name = factor_name

    def _daily_process(self):
        print(self.agent.earth_calender.now_date)
        tem_factor = {'date': self.agent.earth_calender.now_date}
        for comm in self.exchange.contract_dict.keys():
            # 未上市的商品
            if self.exchange.contract_dict[comm].first_listed_date > self.agent.earth_calender.now_date:
                continue
            # 已经退市的商品
            if self.exchange.contract_dict[comm].last_de_listed_date < self.agent.earth_calender.now_date:
                continue

            self.exchange.contract_dict[comm].renew_open_contract(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[comm].renew_operate_contract(now_date=self.agent.earth_calender.now_date)






if __name__ == '__main__':
    cal_factor = CalFactor(
        factor_name='rtn_local',
        begin_date='2010-01-01',
        end_date='2021-02-28',
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO
    )
    cal_factor.test()