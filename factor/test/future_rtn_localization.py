from factor.test.factor_test import FactorTest
from utils.base_para import *
from dateutil.relativedelta import relativedelta
import pandas as pd

pd.set_option('expand_frame_repr', False)


class LongRtnLocalDaily(FactorTest):

    def __init__(self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.f2 = []
        self.f3 = []
        self.f5 = []

    def get_price(self, data):
        data['date'] = data['datetime'].dt.date
        cond1 = data['date'] >= self.agent.earth_calender.now_date
        cond2 = data['date'] <= self.agent.earth_calender.now_date + relativedelta(days=10)

        data = data.loc[cond1 & cond2].copy()
        data = data[['datetime', 'open', 'close']].resample(on='datetime', rule='1D').agg(
            {
                'open': 'first',
                'close': 'last',

            }
        )
        data.dropna(how='any', inplace=True)

        f2_rtn = (data['close'].shift(-2) / data['close']).iloc[0] - 1
        f3_rtn = (data['close'].shift(-3) / data['close']).iloc[0] - 1
        f5_rtn = (data['close'].shift(-5) / data['close']).iloc[0] - 1

        return f2_rtn, f3_rtn, f5_rtn


    def _daily_process(self):
        print(self.agent.earth_calender.now_date)
        tem_f2 = {'date': self.agent.earth_calender.now_date}
        tem_f3 = {'date': self.agent.earth_calender.now_date}
        tem_f5 = {'date': self.agent.earth_calender.now_date}
        for comm in self.exchange.contract_dict.keys():
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
            tem_f2[comm], tem_f3[comm], tem_f5[comm] = self.get_price(data=main_contract_data)

        self.f2.append(tem_f2)
        self.f3.append(tem_f3)
        self.f5.append(tem_f5)



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
    l_f2_df = pd.DataFrame(rtn_local.f2)
    l_f3_df = pd.DataFrame(rtn_local.f3)
    l_f5_df = pd.DataFrame(rtn_local.f5)

    l_f2_df.to_excel(os.path.join(OUTPUT_DATA_PATH, 'f2_rtn.xlsx'))
    l_f3_df.to_excel(os.path.join(OUTPUT_DATA_PATH, 'f3_rtn.xlsx'))
    l_f5_df.to_excel(os.path.join(OUTPUT_DATA_PATH, 'f5_rtn.xlsx'))

