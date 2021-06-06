from raw_backtest.test.main_test import MainTest
import pandas as pd


class SpreadTest(MainTest):
    def __init__(self, test_name, begin_date, end_date, init_cash, contract_list):
        MainTest.__init__(self, test_name, begin_date, end_date, init_cash, contract_list)
        self.t_res_list = []

    def _daily_process(self):
        print(self.agent.earth_calender.now_date)

        for commodity in self.exchange.contract_dict.keys():
            self.exchange.contract_dict[commodity].renew_open_contract(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[commodity].renew_operate_contract(now_date=self.agent.earth_calender.now_date)

        now_open_con = self.exchange.contract_dict['FG'].now_open_contract(now_date=self.agent.earth_calender.now_date)

        near_con = now_open_con[1]
        t_res = {
            'date': self.agent.earth_calender.now_date,
            'main_contract': self.exchange.contract_dict['FG'].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            ),
            'near_con': near_con
        }
        gap_ind = 0
        for far_con in now_open_con[2:-1]:
            near_data = self.exchange.contract_dict['FG'].data_dict[near_con]
            far_data = self.exchange.contract_dict['FG'].data_dict[far_con]
            near_price = near_data.loc[
                near_data['trading_date'] == self.agent.earth_calender.now_date, 'close'
            ].iloc[-1]
            far_price = far_data.loc[
                far_data['trading_date'] == self.agent.earth_calender.now_date, 'close'
            ].iloc[-1]

            if (far_price == 0) or (near_price == 0):
                print(far_con, near_con)
                print(far_price, near_price)
                print(near_data.loc[near_data['trading_date'] == self.agent.earth_calender.now_date])
                raise Exception('=0 error')

            t_res['gap%s' % gap_ind] = far_price - near_price
            gap_ind += 1
            near_con = far_con

        self.t_res_list.append(t_res)

    def output_res(self):
        res_df = pd.DataFrame(self.t_res_list)
        print(res_df)
        res_df.to_excel(r'C:\Users\sycam\Desktop\spread_output_res.xlsx')


if __name__ == '__main__':

    l_contract_list = [
        {
            'id': 'FG',
            'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            'init_margin_rate': 0.15,
            'contract_unit': 20,
            'open_comm': 5,
            'close_comm': 5,
        },
    ]

    main_test = SpreadTest(
        test_name='test',
        begin_date='2012-12-11',
        end_date='2020-12-31',
        init_cash=1000000,
        contract_list=l_contract_list
    )
    main_test.test()
    main_test.output_res()
