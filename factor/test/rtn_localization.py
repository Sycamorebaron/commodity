from factor.test.main_test import MainTest
from utils.base_para import *
from dateutil.relativedelta import relativedelta
import pandas as pd
from sklearn.cluster import KMeans

pd.set_option('expand_frame_repr', False)


class RtnLocalDaily(MainTest):

    def __init__(self, test_name, begin_date, end_date, init_cash, contract_list):
        MainTest.__init__(self, test_name, begin_date, end_date, init_cash, contract_list)
        self.rtn_list = []


    def get_price(self, data):
        data['date'] = data['datetime'].dt.date
        data = data.loc[
            data['date'] == self.agent.earth_calender.now_date
            ]

        day_data = data.loc[data['datetime'].dt.hour <= 15]
        if len(day_data):
            day_open = day_data.loc[
                day_data['datetime'].apply(lambda x: x.strftime('%H:%M') == '09:01'), 'open'
            ].values[0]
            day_close = day_data.loc[
                day_data['datetime'].apply(lambda x: x.strftime('%H:%M') == '15:00'), 'close'
            ].values[0]
        else:
            day_open, day_close = 0, 0

        night_data = data.loc[data['datetime'].dt.hour > 15]

        if len(night_data):
            night_open = night_data.loc[
                night_data['datetime'].apply(lambda x: x.strftime('%H:%M') == '21:01'), 'open'
            ].values[0]
            night_close = night_data.loc[
                night_data['datetime'].apply(lambda x: x.strftime('%H:%M') == '23:00'), 'close'
            ].values[0]
        else:
            night_open, night_close = 0, 0
        return day_open, day_close, night_open, night_close


    def _daily_process(self):
        print(self.agent.earth_calender.now_date)
        tem_rtn = {'date': self.agent.earth_calender.now_date}
        for comm in self.exchange.contract_dict.keys():
            if self.exchange.contract_dict[comm].first_listed_date > self.agent.earth_calender.now_date:
                continue
            if self.exchange.contract_dict[comm].last_de_listed_date < self.agent.earth_calender.now_date:
                continue

            self.exchange.contract_dict[comm].renew_open_contract(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[comm].renew_operate_contract(now_date=self.agent.earth_calender.now_date)

            comm_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            comm_sec_main_contract = self.exchange.contract_dict[comm].now_sec_main_contract(
                now_date=self.agent.earth_calender.now_date
            )

            main_contract_data = self.exchange.contract_dict[comm].data_dict[comm_main_contract]
            sec_main_contract_data = self.exchange.contract_dict[comm].data_dict[comm_sec_main_contract]

            main_day_open, main_day_close, main_night_open, main_night_close = self.get_price(
                data=main_contract_data
            )
            print(comm)
            sec_main_day_open, sec_main_day_close, sec_main_night_open, sec_main_night_close = self.get_price(
                data=sec_main_contract_data
            )

            tem_rtn['%s_main_day_rtn' % comm] = \
                main_day_close / main_day_open - 1 if main_day_open else ''
            tem_rtn['%s_main_night_rtn' % comm] = \
                main_night_close / main_night_open - 1 if main_night_open else ''
            tem_rtn['%s_sec_main_day_rtn' % comm] = \
                sec_main_day_close / sec_main_day_open - 1 if sec_main_day_open else ''
            tem_rtn['%s_sec_main_night_rtn' % comm] = \
                sec_main_night_close / sec_main_night_open - 1 if sec_main_night_open else ''

        self.rtn_list.append(tem_rtn)


if __name__ == '__main__':
    rtn_local = RtnLocalDaily(
        test_name='rtn_local',
        begin_date='2010-01-01',
        end_date='2021-02-28',
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO
    )
    rtn_local.test()
    res_df = pd.DataFrame(rtn_local.rtn_list)
    res_df.to_excel(r'D:\commodity\data\output\daily_rtn.xlsx')
