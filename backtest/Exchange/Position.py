class Position:
    def __init__(self, contract_list):
        self.holding_position = self._init_contract_position(contract_list=contract_list)

    def _init_contract_position(self, contract_list):
        contract_pos = {}
        for contract in contract_list:
            contract_pos[contract['id']] = {}
        return contract_pos
