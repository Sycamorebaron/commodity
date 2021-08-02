from raw_backtest.test.main_test import MainTest
from raw_backtest.Exchange.Contract import Contract
from raw_backtest.Exchange.Exchange import Exchange
import statsmodels.api as sm
import pandas as pd
pd.set_option('expand_frame_repr', False)


class HFContract(Contract):
    def __init__(self, commodity, month_list, init_margin_rate, contract_unit, open_comm, close_comm):
        Contract.__init__(self, commodity, month_list, init_margin_rate, contract_unit, open_comm, close_comm)
        self.hf_data_dict = {}

    def renew_open_contract_hf(self, now_date):
        now_open_contract = self.now_open_contract(now_date=now_date)

        for contract in now_open_contract:
            if contract not in self.hf_data_dict.keys():
                self.hf_data_dict[contract] = self.data_fetcher.get_contract_data_hf(contract=contract)

        _now_ky = list(self.hf_data_dict.keys())
        for contract in _now_ky:
            if contract not in now_open_contract:
                self.hf_data_dict.pop(contract)


class HFExchange(Exchange):
    def __init__(self, init_cash, contract_list):
        Exchange.__init__(self, init_cash, contract_list)

    def _gen_contract(self, contract_info_list):
        contract_dict = {}
        for contract in contract_info_list:
            contract_dict[contract['id']] = HFContract(
                commodity=contract['id'],
                month_list=contract['month_list'],
                init_margin_rate=contract['init_margin_rate'],
                contract_unit=contract['contract_unit'],
                open_comm=contract['open_comm'],
                close_comm=contract['close_comm'],
            )

        return contract_dict


class HFTest(MainTest):
    def __init__(self, test_name, begin_date, end_date, init_cash, contract_list):
        MainTest.__init__(self, test_name, begin_date, end_date, init_cash, contract_list)
        self.exchange = HFExchange(
            contract_list=contract_list,
            init_cash=init_cash
        )
        self.pred_res_list = []

    def _daily_process(self):
        print(self.agent.earth_calender.now_date)

        for commodity in self.exchange.contract_dict.keys():
            self.exchange.contract_dict[commodity].renew_open_contract_hf(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[commodity].renew_operate_contract(now_date=self.agent.earth_calender.now_date)

        fg_main_contract = \
            self.exchange.contract_dict['FG'].now_main_contract(now_date=self.agent.earth_calender.now_date)
        fg_data = self.exchange.contract_dict['FG'].hf_data_dict[fg_main_contract]

        reg_length = 2000
        reg_fg_data = fg_data.loc[
                      fg_data['datetime'] <= self.agent.earth_calender.now_date,
                      ['datetime', 'close']
                  ][-reg_length:].copy()
        test_fg_data = fg_data.loc[fg_data['trading_date'] == self.agent.earth_calender.now_date, ['datetime', 'close']]
        reg_fg_data.columns, test_fg_data.columns = ['datetime', 'fg'], ['datetime', 'fg']

        sa_main_contract = \
            self.exchange.contract_dict['SA'].now_main_contract(now_date=self.agent.earth_calender.now_date)
        sa_data = self.exchange.contract_dict['SA'].hf_data_dict[sa_main_contract]
        reg_sa_data = sa_data.loc[
                      sa_data['datetime'] <= self.agent.earth_calender.now_date,
                      ['datetime', 'close']
                  ][-reg_length:].copy()
        test_sa_data = sa_data.loc[sa_data['trading_date'] == self.agent.earth_calender.now_date, ['datetime', 'close']]
        reg_sa_data.columns, test_sa_data.columns = ['datetime', 'sa'], ['datetime', 'sa']

        reg_merged_data = reg_fg_data.merge(reg_sa_data, on='datetime', how='outer')
        test_merged_data = test_fg_data.merge(test_sa_data, on='datetime', how='outer')

        y = reg_merged_data['sa']
        x = sm.add_constant(reg_merged_data['fg'])
        model = sm.OLS(endog=y, exog=x)
        res = model.fit()
        params = dict(res.params)
        test_merged_data['pred_sa'] = test_merged_data['fg'] * params['fg'] + params['const']
        test_merged_data['e'] = test_merged_data['sa'] - test_merged_data['pred_sa']
        test_merged_data['now_main_sa'] = sa_main_contract
        test_merged_data['now_main_fg'] = fg_main_contract
        test_merged_data['reg_res'] = params['fg']
        self.pred_res_list.append(test_merged_data)

    def output_res(self):

        res_df = pd.concat(self.pred_res_list)
        res_df.reset_index(drop=True, inplace=True)
        res_df['contract_combine'] = res_df['now_main_sa'] + '_' + res_df['now_main_fg']
        combine_list = list(set(list(res_df['contract_combine'])))
        combine_list.sort()
        for combine in combine_list:
            res_df.loc[res_df['contract_combine'] == combine, combine] = res_df['e']
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
        {
            'id': 'SA',
            'month_list': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            'init_margin_rate': 0.15,
            'contract_unit': 20,
            'open_comm': 5,
            'close_comm': 5,
        },
    ]

    main_test = HFTest(
        test_name='cal_factor',
        begin_date='2020-03-01',
        end_date='2020-12-31',
        init_cash=1000000,
        contract_list=l_contract_list
    )
    main_test.test()
    main_test.output_res()
