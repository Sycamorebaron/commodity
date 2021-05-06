from factor.test.main_test import MainTest
from utils.base_para import *
import pandas as pd
from sklearn.decomposition import PCA
import numpy as np
from dateutil.relativedelta import relativedelta
import statsmodels.api as sm
from factor.test.factor_test import FactorTest

pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', 500)


# 休息时间：10:15-10:30
class HFRtn(FactorTest):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.rtn_30t = []

    def resample(self, data, rule):
        data = data.resample(on='datetime', rule=rule).agg(
            {
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
                'open_interest': 'last',
                'total_turnover': 'sum'
            }
        )
        data.dropna(subset=['open'], inplace=True)
        data.reset_index(inplace=True)
        data = data.loc[data['datetime'].apply(lambda x: (x.strftime('%H:%M') != '11:30') & (x.strftime('%H:%M') != '15:00'))]

        return data

    def _daily_process(self):
        print(self.agent.earth_calender.now_date)

        open_comm_list = []

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
            open_comm_list.append(comm)

        daily_rtn_30t = self.t_daily_factor(open_comm_list)

        # 每年保存数据
        if (int(self.agent.earth_calender.now_date.strftime('%m')) >= 12) & (int(self.agent.earth_calender.now_date.strftime('%d')) >= 25):

            rtn_30t = pd.DataFrame(self.rtn_30t)

            rtn_30t.to_excel(
                os.path.join(OUTPUT_DATA_PATH, '%s_std.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )

        self.rtn_30t.append(daily_rtn_30t)

    def t_daily_factor(self, open_comm_list):

        _rtn_df = pd.DataFrame()
        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            if len(today_data):
                data_30t = self.resample(today_data.copy(), rule='30T')
                data_30t['rtn'] = (data_30t['close'] / data_30t['open']) - 1
                data_30t = data_30t[['datetime', 'rtn']]
                data_30t.columns = ['datetime', comm]
                if len(_rtn_df):
                    _rtn_df = _rtn_df.merge(data_30t, on='datetime', how='outer')
                else:
                    _rtn_df = data_30t



        return _rtn_df


if __name__ == '__main__':
    cal_factor = HFRtn(
        factor_name='moment',
        begin_date='2020-01-04',
        end_date='2020-01-10',
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    rtn_30t_df = pd.concat(cal_factor.rtn_30t)
    rtn_30t_df.reset_index(drop=True, inplace=True)
    print(rtn_30t_df)
