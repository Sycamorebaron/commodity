from HF_analyse.HFTest import HFTest
import pandas as pd


class FGFGTest(HFTest):
    def _daily_process(self):
        print(self.agent.earth_calender.now_date)

        for commodity in self.exchange.contract_dict.keys():
            self.exchange.contract_dict[commodity].renew_open_contract_hf(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[commodity].renew_operate_contract(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[commodity].renew_sec_operate_contract(
                now_date=self.agent.earth_calender.now_date
            )

        fg_main_contract = \
            self.exchange.contract_dict['FG'].now_main_contract(now_date=self.agent.earth_calender.now_date)
        fg_sec_main_contract = self.exchange.contract_dict['FG'].now_sec_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        operate_contract_list = [fg_main_contract, fg_sec_main_contract]
        operate_contract_list.sort()
        ope_con_1 = operate_contract_list[0]
        ope_con_2 = operate_contract_list[1]
        ope_con_1_data = self.exchange.contract_dict['FG'].hf_data_dict[ope_con_1]
        ope_con_2_data = self.exchange.contract_dict['FG'].hf_data_dict[ope_con_2]

        ope_con_1_test_data = ope_con_1_data.loc[
            ope_con_1_data['trading_date'] == self.agent.earth_calender.now_date, ['datetime', 'close']
        ]
        ope_con_2_test_data = ope_con_2_data.loc[
            ope_con_2_data['trading_date'] == self.agent.earth_calender.now_date, ['datetime', 'close']
        ]
        ope_con_1_test_data.columns, ope_con_2_test_data.columns = ['datetime', 'con1'], ['datetime', 'con2']
        merged_data = ope_con_1_test_data.merge(ope_con_2_test_data, on='datetime', how='outer')
        # merged_data['con1'] = ope_con_1
        # merged_data['con2'] = ope_con_2
        merged_data['combine_con'] = ope_con_1 + '_' + ope_con_2
        merged_data['gap'] = merged_data['con2'] - merged_data['con1']
        self.pred_res_list.append(merged_data)

    def output_res(self):
        res_df = pd.concat(self.pred_res_list)
        res_df.reset_index(drop=True, inplace=True)
        combine_con_list = list(set(list(res_df['combine_con'])))
        for combine_con in combine_con_list:
            res_df.loc[res_df['combine_con'] == combine_con, combine_con] = res_df['gap']
        print(res_df)
        res_df.to_excel(r'C:\Users\sycam\Desktop\output_res.xlsx')


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

    main_test = FGFGTest(
        test_name='test',
        begin_date='2020-03-01',
        end_date='2020-12-31',
        init_cash=1000000,
        contract_list=l_contract_list
    )
    main_test.test()
    main_test.output_res()
