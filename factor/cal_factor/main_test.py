from factor.Exchange.Exchange import Exchange
from factor.Agent.Agent import Agent
from factor.Agent.Strategy import MAStrategy
from utils.base_para import OUTPUT_DATA_PATH, local_data_path
import os


class MainTest:
    def __init__(
        self, test_name, begin_date, end_date, init_cash, contract_list, local_data_path, leverage=True
    ):
        self.test_name = test_name
        self._begin_date = begin_date
        self.end_date = end_date

        self.exchange = Exchange(
            contract_list=contract_list,
            init_cash=init_cash,
            local_data_path=local_data_path
        )
        self.agent = self._gen_agent(begin_date=begin_date, end_date=end_date, leverage=leverage)

    def _gen_agent(self, begin_date, end_date, leverage):
        return Agent(
            strategy=MAStrategy(
                ma_para_list=[5, 10, 20, 60, 120]
            ),
            begin_date=begin_date,
            end_date=end_date,
            leverage=leverage,
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
                now_dt=self.agent.earth_calender.now_date
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
            now_dt=self.agent.earth_calender.now_date
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
