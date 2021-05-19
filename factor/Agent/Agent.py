from factor.Agent.Recorder import Recorder
from factor.Agent.TradeCenter import TradeCenter
from factor.Agent.EarthCalender import EarthCalender
import string


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

        now_equity = exchange.account.equity

        target_num = {}
        for contract in target_pos.keys():
            contract_price = exchange.contract_dict[contract.rstrip(string.digits)].get_contract_data(
                contract=contract,
                now_date=self.earth_calender.now_date
            )
            contract_init_margin = \
                contract_price * exchange.contract_dict[contract.rstrip(string.digits)].init_margin_rate * \
                exchange.contract_dict[contract.rstrip(string.digits)].contract_unit
            target_num[contract] = int(now_equity * target_pos[contract] / contract_init_margin)

        trade_info = self.trade_center.trade(
            exchange=exchange,
            target_num=target_num,
            now_date=self.earth_calender.now_date
        )
        return trade_info

    def contract_move_forward(self, exchange, now_operate_contract, new_operate_contract, now_date):
        # 移仓换月
        print('CONTRACT MOVE FORWARD', now_operate_contract, new_operate_contract)
        now_holding_num = exchange.account.position.holding_position[now_operate_contract.strip('1234567890')][
            now_operate_contract]['num']
        self.trade_center.trade(
            exchange=exchange,
            target_num={
                now_operate_contract: 0,
                new_operate_contract: now_holding_num
            },
            now_date=now_date
        )
