from backtest.Exchange.Exchange import Exchange
from backtest.Agent.Agent import Agent
from backtest.Agent.Strategy import MAStrategy


class MainTest:
    def __init__(self, begin_date, end_date, init_cash, contract_list):
        self._begin_date = begin_date
        self.end_date = end_date
        self.exchange = Exchange(
            contract_list=contract_list,
            init_cash=init_cash
        )
        self.agent = Agent(
            strategy=MAStrategy(
                ma_para_list=[5, 10, 20, 60, 120]
            ),
            begin_date=begin_date,
            end_date=end_date,
        )

    def test(self):

        while not self.agent.earth_calender.end_of_test():
            # 交易日
            if self.exchange.trade_calender.tradable_date(date=self.agent.earth_calender.now_date):

                now_operate_contract = self.exchange.contract_dict['M'].operate_contract
                self.exchange.contract_dict['M'].renew_open_contract(now_date=self.agent.earth_calender.now_date)
                self.exchange.contract_dict['M'].renew_operate_contract(now_date=self.agent.earth_calender.now_date)
                new_operate_contract = self.exchange.contract_dict['M'].operate_contract

                if (now_operate_contract != '') & (now_operate_contract != new_operate_contract):
                    self.agent.contract_move_forward(
                        exchange=self.exchange,
                        now_operate_contract=now_operate_contract,
                        new_operate_contract=new_operate_contract,
                        now_date=self.agent.earth_calender.now_date
                    )

                # 根据策略计算目标仓位
                target_pos = self.agent.strategy.cal_target_pos(
                    contract=self.exchange.contract_dict['M'],
                    tm=self.agent.earth_calender.now_date
                )
                print(target_pos)
                # 根据目标仓位调仓
                trade_info = self.agent.change_position(
                    exchange=self.exchange,
                    target_pos=target_pos,
                )

                # 每日结算
                self.exchange.account.daily_settlement(
                    now_date=self.agent.earth_calender.now_date,
                    contract_dict=self.exchange.contract_dict
                )

                print('*' * 30)
                print('DATE', self.agent.earth_calender.now_date)
                print('POSITION', self.exchange.account.position.holding_position)
                print('CASH', self.exchange.account.cash)
                print('EQUITY', self.exchange.account.equity)
                print('RISK RATE', self.exchange.account.risk_rate)
                print('*' * 30)
                print('=' * 50)
            self.agent.earth_calender.next_day()


if __name__ == '__main__':
    main_test = MainTest(
        begin_date='2011-01-01',
        end_date='2020-11-26',
        init_cash=1000000,
        contract_list=[
                {
                    'id': 'M',
                    'month_list': [1, 3, 5, 7, 8, 9, 11, 12],
                    'init_margin_rate': 0.15,
                    'contract_unit': 20,
                    'open_comm': 5,
                    'close_comm': 5,
                },
            ]
    )
    main_test.test()
