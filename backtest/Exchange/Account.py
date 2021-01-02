from backtest.Exchange.Position import Position
from backtest.Infras.DataFetcher import DataFetcher
from utils.base_para import *


class Account:
    def __init__(self, init_cash, contract_list):
        self.cash = init_cash
        self.position = Position(contract_list=contract_list)
        self.data_fetcher = DataFetcher(database=eg)
        self.risk_rate = 0
        self.equity = init_cash

    def daily_settlement(self, now_date, contract_dict):
        for commodity in self.position.holding_position:
            pos_dict = self.position.holding_position[commodity]
            # 更新每个持仓合约的盈亏
            for contract in pos_dict:
                commodity_contract = contract_dict[contract.strip('1234567890')]
                data = commodity_contract.data_dict[contract]
                latest_price = data.loc[data['trading_date'] == now_date, 'close'].iloc[-1]
                print('account.daily_settlement', contract, latest_price)
                latest_pnl = \
                    (latest_price - pos_dict[contract]['hold_price']) * pos_dict[contract]['num'] * \
                    commodity_contract.contract_unit

                latest_use_margin = \
                    latest_price * commodity_contract.contract_unit * commodity_contract.init_margin_rate * \
                    abs(pos_dict[contract]['num'])

                # 释放多余的保证金
                self.cash += (pos_dict[contract]['use_margin'] - latest_use_margin)
                # 更新每个持仓合约的pnl，持仓价格，所需保证金
                self.position.holding_position[commodity][contract]['pnl'] = latest_pnl
                self.position.holding_position[commodity][contract]['hold_price'] = latest_price
                self.position.holding_position[commodity][contract]['use_margin'] = latest_use_margin

        # 计算当前的权益
        sum_pnl, sum_margin = 0, 0
        for commodity in self.position.holding_position:
            pos_dict = self.position.holding_position[commodity]
            for contract in pos_dict:
                sum_pnl += pos_dict[contract]['pnl']
                sum_margin += pos_dict[contract]['use_margin']

        self.equity = self.cash + sum_margin + sum_pnl

        self.risk_rate = sum_margin / self.equity

        if self.risk_rate >= 0.999:
            raise Exception('RISK RATE TOO HIGH!')

        # 合约浮动盈亏落地
        for commodity in self.position.holding_position:
            pos_dict = self.position.holding_position[commodity]
            for contract in pos_dict:
                print('account.daily_settlement', self.position.holding_position[commodity][contract], self.cash)

                self.cash += pos_dict[contract]['pnl']
                self.position.holding_position[commodity][contract]['pnl'] = 0

