from backtest.Exchange.Contract import Contract
from backtest.Exchange.Position import Position
from backtest.Exchange.TradeCalender import TradeCalender


class Exchange:
    def __init__(self, contract_list):
        self._gen_contract(contract_list)
        self.position = Position(contract_list)
        self.trade_calender = TradeCalender()

    def _gen_contract(self, contract_info_list):
        for contract in contract_info_list:
            print("LOAD CONTRACT", contract)
            self.__dict__['%s_contract' % contract['id']] = Contract(
                contract_name=contract['id'],
                month_list=contract['month_list']
            )


if __name__ == '__main__':

    exchange = Exchange(
        contract_list=[
            {
                'id': 'M',
                'month_list': [1, 3, 5, 7, 8, 9, 11, 12]
            },
        ]
    )
    ope_con = exchange.M_contract.renew_operate_contract(now_contract='M1905', now_date='2019-11-25')

    print(ope_con)
