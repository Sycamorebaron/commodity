class TradeCenter:
    def __init__(self):
        pass

    def close(self, contract_id, close_num):
        pass

    def open(self, contract_id, open_num):
        pass

    def trade(self, exchange, target_num):

        for contract_target_num in target_num.keys():

            contract_holding_pos = exchange.account.position.holding_position
            print(contract_target_num, contract_holding_pos)
            exit()

        pass
