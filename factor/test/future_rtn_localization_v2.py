from factor.test.factor_test import FactorTest
from utils.base_para import *
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np

pd.set_option('expand_frame_repr', False)


class LongRtnLocalDaily(FactorTest):

    def __init__(self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.f3_high = []
        self.f3_low = []
        self.f5_high = []
        self.f5_low = []

    def get_price(self, data):
        data['date'] = data['datetime'].dt.date
        cond1 = data['date'] >= self.agent.earth_calender.now_date
        cond2 = data['date'] <= self.agent.earth_calender.now_date + relativedelta(days=31)

        data = data.loc[cond1 & cond2].copy()
        data = data[['order_book_id', 'datetime', 'open', 'high', 'low', 'close']].resample(on='datetime', rule='1D').agg(
            {
                'order_book_id': 'last',
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
            }
        )
        data.dropna(how='any', inplace=True)
        print(data)
        try:
            f3_high = (data['high'].rolling(3).max() / data['close'].shift(3) - 1).iloc[4]
        except Exception as e:
            f3_high = np.nan
        try:
            f3_low = (data['low'].rolling(3).max() / data['close'].shift(3) - 1).iloc[4]
        except Exception as e:
            f3_low = np.nan
        try:
            f5_high = (data['high'].rolling(5).max() / data['close'].shift(5) - 1).iloc[6]
        except Exception as e:
            f5_high = np.nan
        try:
            f5_low = (data['low'].rolling(5).max() / data['close'].shift(5) - 1).iloc[6]
        except Exception as e:
            f5_low = np.nan

        return f3_high, f3_low, f5_high, f5_low


    def _daily_process(self):
        print(self.agent.earth_calender.now_date)

        tem_f3_high = {'date': self.agent.earth_calender.now_date}
        tem_f3_low = {'date': self.agent.earth_calender.now_date}
        tem_f5_high = {'date': self.agent.earth_calender.now_date}
        tem_f5_low = {'date': self.agent.earth_calender.now_date}

        for comm in self.exchange.contract_dict.keys():
            if self.agent.earth_calender.now_date > \
                pd.to_datetime(self.exchange.contract_dict[comm].last_de_listed_date) - relativedelta(months=1):
                continue

            if self.exchange.contract_dict[comm].first_listed_date > self.agent.earth_calender.now_date:
                continue
            if self.exchange.contract_dict[comm].last_de_listed_date < self.agent.earth_calender.now_date:
                continue

            self.exchange.contract_dict[comm].renew_main_contract(now_date=self.agent.earth_calender.now_date)

            comm_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )

            main_contract_data = self.exchange.contract_dict[comm].data_dict[comm_main_contract]
            print(comm)
            tem_f3_high[comm], tem_f3_low[comm], tem_f5_high[comm], tem_f5_low[comm] = \
                self.get_price(data=main_contract_data)

        self.f3_high.append(tem_f3_high)
        self.f3_low.append(tem_f3_low)
        self.f5_high.append(tem_f5_high)
        self.f5_low.append(tem_f5_low)


if __name__ == '__main__':
    rtn_local = LongRtnLocalDaily(
        test_name='rtn_local',
        begin_date='2010-01-01',
        end_date='2021-01-31',
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path = local_data_path_5T
    )

    rtn_local.test()
    l_f3_high = pd.DataFrame(rtn_local.f3_high)
    l_f3_low = pd.DataFrame(rtn_local.f3_low)
    l_f5_high = pd.DataFrame(rtn_local.f5_high)
    l_f5_low = pd.DataFrame(rtn_local.f5_low)


    l_f3_high.to_excel(os.path.join(OUTPUT_DATA_PATH, 'f3_high.xlsx'))
    l_f3_low.to_excel(os.path.join(OUTPUT_DATA_PATH, 'f3_low.xlsx'))
    l_f5_high.to_excel(os.path.join(OUTPUT_DATA_PATH, 'f5_high.xlsx'))
    l_f5_low.to_excel(os.path.join(OUTPUT_DATA_PATH, 'f5_low.xlsx'))

