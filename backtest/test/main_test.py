from backtest.exchange.exchange import Exchange
from backtest.agent.agent import Agent

class MainTest:
    def __init__(self):
        self.exchange = Exchange()
        self.agent = Agent()

    def test(self):
        pass



if __name__ == '__main__':
    main_test = MainTest()

