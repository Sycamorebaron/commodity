from factor.Exchange.Contract import Contract
from factor.Exchange.Account import Account
from factor.Exchange.TradeCalender import TradeCalender


class Exchange:
    def __init__(self, init_cash, contract_list, local_data_path):
        self.contract_dict = self._gen_contract(
            contract_info_list=contract_list,
            local_data_path=local_data_path
        )
        self.account = Account(
            init_cash=init_cash,
            contract_list=contract_list
        )
        self.trade_calender = TradeCalender(local_data_path=local_data_path)

    def _gen_contract(self, contract_info_list, local_data_path):
        contract_dict = {}
        for contract in contract_info_list:

            contract_dict[contract['id']] = Contract(
                commodity=contract['id'],
                first_listed_date=contract['first_listed_date'],
                last_de_listed_date=contract['last_de_listed_date'],
                month_list=contract['month_list'],
                init_margin_rate=contract['init_margin_rate'],
                contract_unit=contract['contract_unit'],
                open_comm=contract['open_comm'],
                close_comm=contract['close_comm'],
                local_data_path=local_data_path
            )

        return contract_dict

    def renew_account(self):
        pass

