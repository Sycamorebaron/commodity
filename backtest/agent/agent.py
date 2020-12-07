from backtest.agent.strategy import Strategy
from backtest.agent.recorder import Recorder
from backtest.agent.trade_center import TradeCenter

class Agent:
    def __init__(self):
        self.strategy = Strategy()
        self.recorder = Recorder()
        self.trade_center = TradeCenter()

