from backtest.Exchange.Position import Position
from backtest.Infras.DataFetcher import DataFetcher
from utils.base_para import *


class Account:
    def __init__(self, init_cash, contract_list):
        self.cash = init_cash
        self.position = Position(contract_list=contract_list)
        self.data_fetcher = DataFetcher(database=eg)

    def now_equity(self, now_date, data_dict):
        """
        用今收更新当前权益
        :return:
        """
        pnl = 0
        print(self.position.holding_position)
        # for comm in self.position.holding_position.keys():
        #     for position in self.position.holding_position[comm]:
        exit()


        pass