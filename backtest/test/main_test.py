from backtest.Exchange.Exchange import Exchange
from backtest.Agent.Agent import Agent
from backtest.Agent.Strategy import MAStrategy
from utils.base_para import OUTPUT_DATA_PATH
import os


class MainTest:
    def __init__(self, test_name, begin_date, end_date, init_cash, contract_list):
        self.test_name = test_name
        self._begin_date = begin_date
        self.end_date = end_date
        self.exchange = Exchange(
            contract_list=contract_list,
            init_cash=init_cash
        )
        self.agent = self._gen_agent(begin_date=begin_date, end_date=end_date)

    def _gen_agent(self, begin_date, end_date):
        return Agent(
            strategy=MAStrategy(
                ma_para_list=[5, 10, 20, 60, 120]
            ),
            begin_date=begin_date,
            end_date=end_date,
        )

    def _daily_process(self):
        """
        每日进行的流程
        :return:
        """
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
        # 记录交易
        self.agent.recorder.record_trade(info=trade_info)

        # 每日结算
        self.exchange.account.daily_settlement(
            now_date=self.agent.earth_calender.now_date,
            contract_dict=self.exchange.contract_dict
        )

        # 记录资金情况
        self.agent.recorder.record_equity(
            info={
                'date': self.agent.earth_calender.now_date,
                'target_pos': target_pos,
                'position': self.exchange.account.position.holding_position,
                'cash': self.exchange.account.cash,
                'equity': self.exchange.account.equity,
                'risk_rate': self.exchange.account.risk_rate
            }
        )

        print('*' * 30)
        print('DATE', self.agent.earth_calender.now_date)
        print('POSITION', self.exchange.account.position.holding_position)
        print('CASH', self.exchange.account.cash)
        print('EQUITY', self.exchange.account.equity)
        print('RISK RATE', self.exchange.account.risk_rate)
        print('*' * 30)
        print('=' * 50)

    def test(self):

        while not self.agent.earth_calender.end_of_test():
            # 交易日
            if self.exchange.trade_calender.tradable_date(date=self.agent.earth_calender.now_date):
                self._daily_process()
            self.agent.earth_calender.next_day()

        self.agent.recorder.equity_curve().to_csv(os.path.join(OUTPUT_DATA_PATH, '%s_equity_curve.csv' % self.test_name))
        self.agent.recorder.trade_hist().to_csv(os.path.join(OUTPUT_DATA_PATH, '%s_trade_hist.csv' % self.test_name))

if __name__ == '__main__':
    main_test = MainTest(
        test_name='test',
        begin_date='2011-01-01',
        end_date='2012-11-26',
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
