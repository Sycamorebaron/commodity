from backtest.Agent.Recorder import Recorder
from backtest.Agent.TradeCenter import TradeCenter
from backtest.Agent.EarthCalender import EarthCalender


class Agent:
    def __init__(self, strategy, begin_date, end_date):
        self.strategy = strategy
        self.recorder = Recorder()
        self.trade_center = TradeCenter()
        self.earth_calender = EarthCalender(begin_date=begin_date, end_date=end_date)

    def change_position(self, exchange, target_pos):
        """
        根据target pos计算应交易合约张数
        :param exchange:
        :param target_pos:
        :return:
        """
        target_num = target_pos

        trade_info = self.trade_center.trade(
            exchange=exchange,
            target_num=target_num
        )
