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
                commodity=contract['id'],
                month_list=contract['month_list'],
                init_margin_rate=contract['init_margin_rate'],
                contract_unit=contract['contract_unit'],
                open_comm=contract['open_comm'],
                close_comm=contract['close_comm'],
            )

        return contract_dict

    def renew_account(self):
        pass

