from backtest.Exchange.Position import Position
from backtest.Infras.DataFetcher import DataFetcher
from utils.base_para import *


class Account:
    def __init__(self, init_cash, contract_list):
        self.cash = init_cash
        self.position = Position(contract_list=contract_list)
        self.data_fetcher = DataFetcher(database=eg)
        self.risk_rate = 0
        self.equity = init_cash

    def now_equity(self, now_date, data_dict):
        """
        用今收更新当前权益
        :return:
        """
        pnl = 0
        print(self.position.holding_position)
        for commodity in self.position.holding_position.keys():
            if self.position.holding_position[commodity] == {}:
                return self.cash
            for position in self.position.holding_position[commodity]:
                print(position)
            exit()
