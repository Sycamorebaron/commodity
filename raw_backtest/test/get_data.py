import pandas as pd
from raw_backtest.test.main_test import MainTest
pd.set_option('expand_frame_repr', False)


class GetData(MainTest):
    def __init__(self, test_name, begin_date, end_date, init_cash, contract_list):
        MainTest.__init__(self, test_name, begin_date, end_date, init_cash, contract_list)
        self.return_list = []

    def _daily_process(self):
        today_return = {'date': self.agent.earth_calender.now_date}
        for comm in self.exchange.contract_dict.keys():
            self.exchange.contract_dict[comm].renew_open_contract(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[comm].renew_operate_contract(now_date=self.agent.earth_calender.now_date)
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            now_sec_contract = self.exchange.contract_dict[comm].now_sec_main_contract(
                now_date=self.agent.earth_calender.now_date
            )


            main_data = self.exchange.contract_dict[comm].data_dict[now_main_contract][[
                'datetime', 'close'
            ]]
            main_data.columns = ['datetime', 'main']
            sec_data = self.exchange.contract_dict[comm].data_dict[now_sec_contract][[
                'datetime', 'close'
            ]]
            sec_data.columns = ['datetime', 'sec']

            data = main_data.merge(sec_data, on='datetime', how='outer')

            data = data.resample(on='datetime', rule='1D').agg(
                {
                    'main': 'last',
                    'sec': 'last'
                }
            )
            data = data.loc[data.index <= self.agent.earth_calender.now_date]
            data = data.fillna(method='ffill')
            data['gap'] = data['main'] - data['sec']

            today_return[comm + '_gap'] = data['gap'].iloc[-1] / data['gap'].iloc[-2] - 1
        print(today_return)
        self.return_list.append(today_return)


if __name__ == '__main__':

    l_contract_list = [
        # {
        #     'id': 'FG',
        #     'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        #     'init_margin_rate': 0.15,
        #     'contract_unit': 20,
        #     'open_comm': 5,
        #     'close_comm': 5,
        # },
        {
            'id': 'SA',
            'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            'init_margin_rate': 0.15,
            'contract_unit': 20,
            'open_comm': 5,
            'close_comm': 5,
        },
    ]

    get_data = GetData(
        test_name='get_data',
        begin_date='2020-01-01',
        end_date='2021-01-01',
        init_cash=1000000,
        contract_list=l_contract_list
    )
    get_data.test()
    return_df = pd.DataFrame(get_data.return_list)
    return_df.to_excel(r'D:\chemical_price_pred\data\SA_gap.xlsx')
    print(return_df)
