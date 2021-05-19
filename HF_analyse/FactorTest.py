from HF_analyse.HFTest import HFTest
from utils.base_para import NORMAL_CONTRACT_INFO
import pandas as pd


class MomentumFactorTest(HFTest):
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
        # merged_data['con 1'] = ope_con_1
        # merged_data['con2'] = ope_con_2
        merged_data['combine_con'] = ope_con_1 + '_' + ope_con_2
        merged_data['gap'] = merged_data['con2'] - merged_data['con1']
        self.pred_res_list.append(merged_data)


if __name__ == '__main__':

    main_test = MomentumFactorTest(
        test_name='test',
        begin_date='2011-01-01',
        end_date='2020-12-31',
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO
    )
    main_test.test()
    main_test.output_res()
