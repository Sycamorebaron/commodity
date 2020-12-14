class TradeCenter:
    def __init__(self):
        pass

    def close(self, contract_id, close_num):
        pass

    def open(self, contract_id, open_num):
        pass

    def trade(self, exchange, target_num):

        for ctr_id in target_num.keys():
            ctr_target_pos = target_num[ctr_id]

            ctr_holding_pos = exchange.position.holding_position

        print(target_num)
        print(exchange.position.holding_position)
        print('M1109'.strip('0123456789'))
        exit()
        pass
