import sys,os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(BASE_DIR)
sys.path.append(BASE_DIR)

from factor.test.main_test import MainTest
from utils.base_para import *
import pandas as pd

pd.set_option('expand_frame_repr', False)


class CalFactor(MainTest):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        MainTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.mean = []
        self.std = []
        self.skew = []
        self.kurt = []
        self.factor_name = factor_name

    def _daily_process(self):
        print(self.agent.earth_calender.now_date)
        tem_mean = {'date': self.agent.earth_calender.now_date}
        tem_std = {'date': self.agent.earth_calender.now_date}
        tem_skew = {'date': self.agent.earth_calender.now_date}
        tem_kurt = {'date': self.agent.earth_calender.now_date}
        for comm in self.exchange.contract_dict.keys():
            # 未上市的商品
            if self.exchange.contract_dict[comm].first_listed_date > self.agent.earth_calender.now_date:
                continue
            # 已经退市的商品
            if self.exchange.contract_dict[comm].last_de_listed_date < self.agent.earth_calender.now_date:
                continue
            print(comm)

            self.exchange.contract_dict[comm].renew_open_contract(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[comm].renew_operate_contract(now_date=self.agent.earth_calender.now_date)

            tem_mean[comm], tem_std[comm], tem_skew[comm], tem_kurt[comm] = self.t_factor(comm)

        self.mean.append(tem_mean)
        self.std.append(tem_std)
        self.skew.append(tem_skew)
        self.kurt.append(tem_kurt)


    def t_factor(self, comm):

        now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
        today_data = _data.loc[_data['datetime'].apply(
            lambda x: x.strftime('%Y-%m-%d') == self.agent.earth_calender.now_date.strftime('%Y-%m-%d')
        )]

        today_data = today_data.resample(on='datetime', rule='5T').agg(
            {
                'order_book_id': 'last',
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
                'open_interest': 'last',
                'total_turnover': 'sum'
            }
        )
        today_data['rtn'] = today_data['close'] / today_data['open'] - 1
        return today_data['rtn'].mean(), today_data['rtn'].std(ddof=1), today_data['rtn'].skew(), today_data['rtn'].kurtosis()


if __name__ == '__main__':
    cal_factor = CalFactor(
        factor_name='moment',
        begin_date='2010-01-04',
        end_date='2021-02-28',
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    mean_df = pd.DataFrame(cal_factor.mean)
    std_df = pd.DataFrame(cal_factor.std)
    skew_df = pd.DataFrame(cal_factor.skew)
    kurt_df = pd.DataFrame(cal_factor.kurt)
    mean_df.to_csv(os.path.join(OUTPUT_DATA_PATH, 'factor_mean.xlsx'))
    std_df.to_csv(os.path.join(OUTPUT_DATA_PATH, 'factor_std.xlsx'))
    skew_df.to_csv(os.path.join(OUTPUT_DATA_PATH, 'factor_skew.xlsx'))
    kurt_df.to_csv(os.path.join(OUTPUT_DATA_PATH, 'factor_kurt.xlsx'))
