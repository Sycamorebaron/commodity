from factor.Agent.Recorder import Recorder
from factor.Agent.TradeCenter import TradeCenter
from factor.Agent.EarthCalender import EarthCalender
import string
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, 'Timer', round(end-start, 4))
        return res
    return wrapper


class Agent:
    def __init__(self, strategy, begin_date, end_date, leverage):
        self.strategy = strategy
        self.recorder = Recorder()
        self.trade_center = TradeCenter()
        self.earth_calender = EarthCalender(begin_date=begin_date, end_date=end_date)
        self.leverage = leverage

    def change_position(self, exchange, target_pos, now_dt, field='close'):
        """
        根据target pos计算应交易合约张数
        :param exchange:
        :param target_pos:
        :return:
        """
        now_equity = exchange.account.equity
        target_num = {}
        for contract in target_pos.keys():
            contract_price = exchange.contract_dict[contract.rstrip(string.digits)]._get_contract_data(
                contract=contract,
                dt=now_dt,
                field=field,
            )

            if self.leverage:
                contract_init_margin = \
                    contract_price * (exchange.contract_dict[contract.rstrip(string.digits)].init_margin_rate) * \
                    exchange.contract_dict[contract.rstrip(string.digits)].contract_unit
            else:
                contract_init_margin = contract_price * \
                                       exchange.contract_dict[contract.rstrip(string.digits)].contract_unit

            # print(contract_init_margin, contract)

            target_num[contract] = int(now_equity * target_pos[contract] / contract_init_margin)

        trade_info = self.trade_center.trade(
            exchange=exchange,
            target_num=target_num,
            now_dt=now_dt,
            field=field
        )
        return trade_info

    def contract_move_forward(self, exchange, now_operate_contract, new_operate_contract, now_dt):
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
            now_dt=now_dt
        )
