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

        data_dict = {}
        for obj in exchange.__dict__:
            if obj.endswith('contract'):
                data_dict = {**data_dict, **exchange.__dict__[obj].data_dict}

        now_equity = exchange.account.now_equity(
            now_date=self.earth_calender.now_date,
            data_dict=data_dict
        )

        exit()
        trade_info = self.trade_center.trade(
            exchange=exchange,
            target_num=target_num
        )
