from backtest.Exchange.Contract import Contract
from backtest.Exchange.Account import Account
from backtest.Exchange.TradeCalender import TradeCalender


class Exchange:
    def __init__(self, init_cash, contract_list):
        self.contract_dict = self._gen_contract(
            contract_info_list=contract_list
        )
        self.account = Account(
            init_cash=init_cash,
            contract_list=contract_list
        )
        self.trade_calender = TradeCalender()

    def _gen_contract(self, contract_info_list):
        contract_dict = {}
        for contract in contract_info_list:

            contract_dict[contract['id']] = Contract(
                contract_name=contract['id'],
                month_list=contract['month_list'],
                init_margin_rate=contract['init_margin_rate'],
                contract_unit=contract['contract_unit']
            )

        return contract_dict

    def renew_account(self):
        pass


if __name__ == '__main__':

    exchange = Exchange(
        contract_list=[
            {
                'id': 'M',
                'month_list': [1, 3, 5, 7, 8, 9, 11, 12]
            },
        ],
        init_cash=10000000
    )
    ope_con = exchange.M_contract.renew_operate_contract(now_contract='M1905')

    print(ope_con)
