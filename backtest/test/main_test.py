from backtest.exchange.exchange import Exchange
from backtest.agent.agent import Agent
from backtest.exchange.earth_calender import EarthCalender


class MainTest:
    def __init__(self, begin_date, end_date):
        self._begin_date = begin_date
        self.end_date = end_date
        self.earth_calender = EarthCalender(
            begin_date=begin_date,
            end_date=end_date
        )
        self.exchange = Exchange()
        self.agent = Agent()

    def test(self):
        # 交易日
        while self.exchange.trade_calender.tradable_date(date=self.earth_calender.now_date):
            self.exchange.contract.renew_contract()
            # 当前有持仓，且操作合约不是operate contract，平仓
            if self.exchange.position.holding_position:
                if self.exchange.position.holding_position[0]['contract_id'] != self.exchange.contract.operate_contract:
                    self.agent.trade_center.close_position()
            




if __name__ == '__main__':
    main_test = MainTest(
        begin_date='2011-01-01',
        end_date='2020-11-31'
    )
    main_test.test()

