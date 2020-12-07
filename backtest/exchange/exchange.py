from backtest.exchange.contract import Contract
from backtest.exchange.position import Position
from backtest.exchange.data_center import DataCenter
from backtest.exchange.trade_calender import TradeCalender

class Exchange:
    def __init__(self):
        self.contract = Contract()
        self.position = Position()
        self.data_center = DataCenter()
        self.trade_calender = TradeCalender()
