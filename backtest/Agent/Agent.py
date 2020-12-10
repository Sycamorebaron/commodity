from backtest.Agent.Recorder import Recorder
from backtest.Agent.TradeCenter import TradeCenter
from backtest.Agent.EarthCalender import EarthCalender


class Agent:
    def __init__(self, strategy, begin_date, end_date):
        self.strategy = strategy
        self.recorder = Recorder()
        self.trade_center = TradeCenter()
        self.earth_calender = EarthCalender(begin_date=begin_date, end_date=end_date)
