import string


class TradeCenter:

    @staticmethod
    def _open(exchange, contract, num, price, now_date):
        """
        纯开，equity和cash减掉开仓手续费（按张），记录开仓信息（时间，价格，数量），风险度在最外层更新，每日结算时更新renew_price
        :param exchange:
        :param num: 可正可负
        :param price:
        :return:
        """
        commodity = contract.strip('0123456789')
        open_margin = \
            exchange.contract_dict[commodity].contract_unit * \
            exchange.contract_dict[commodity].init_margin_rate * price * abs(num)
        print('OPEN', now_date, contract, num, price)
        exchange.account.cash -= (
                open_margin + abs(num) * exchange.contract_dict[commodity].open_comm
        )
        exchange.account.equity -= abs(num) * exchange.contract_dict[commodity].open_comm
        exchange.account.position.holding_position[commodity][contract] = {
            'open_date': now_date,
            'use_margin': open_margin,
            'open_price': price,  # 开仓均价
            'renew_price': price,  # 每日结算持仓均价
            'num': num,
            'pnl': 0,
        }

    @staticmethod
    def _close(exchange, contract, price, now_date):
        """
        纯平，平掉某个合约所有仓位，equity和cash减掉平仓手续费，去掉position，计算盈亏，风险度在最外层更新
        :param exchange:
        :param price:
        :return:
        """
        commodity = contract.strip('0123456789')
        num = exchange.account.position.holding_position[commodity][contract]['num']
        use_margin = exchange.account.position.holding_position[commodity][contract]['use_margin']
        today_profit = (price - exchange.account.position.holding_position[commodity][contract]['renew_price']) * num
        print('CLOSE', now_date, contract, num, price)
        exchange.account.cash += today_profit + use_margin
        exchange.equity += today_profit

        exchange.account.cash -= exchange.contract_dict[commodity].close_comm
        exchange.account.equity -= exchange.contract_dict[commodity].close_comm

        exchange.account.position.drop(contract=contract)

    def _inc(self, exchange, contract, num, price, now_date):
        """
        加仓，含加多和加空
        :param exchange:
        :param num:
        :param price:
        :return:
        """
        pass

    def _dec(self, exchange, contract, num, price, now_date):
        """
        减仓，含减多和减空
        :param exchange:
        :param num:
        :param price:
        :return:
        """
        pass

    def trade(self, exchange, target_num, now_date):

        for contract in target_num.keys():

            if contract in exchange.account.position.holding_position[contract.rstrip(string.digits)].keys():
                hold_num = exchange.account.position.holding_position[contract.rstrip(string.digits)][contract]
            else:
                hold_num = 0
            price = exchange.contract_dict[contract.rstrip(string.digits)].get_contract_data(contract, now_date)

            # 无持仓
            if hold_num == 0:
                # 开多
                if target_num[contract] > 0:
                    self._open(exchange=exchange, contract=contract, num=target_num[contract], price=price,
                               now_date=now_date)
                # 开空
                elif target_num[contract] < 0:
                    self._open(exchange=exchange, contract=contract, num=target_num[contract], price=price,
                               now_date=now_date)
            # 持有多头
            elif hold_num > 0:
                # 加多
                if target_num[contract] > hold_num:
                    self._inc(exchange=exchange, contract=contract, num=target_num[contract] - hold_num, price=price,
                              now_date=now_date)
                # 减多
                elif (target_num[contract] < hold_num) & (target_num[contract] > 0):
                    self._dec(exchange=exchange, contract=contract, num=target_num[contract] - hold_num, price=price,
                              now_date=now_date)
                # 平多
                elif target_num[contract] == 0:
                    self._close(exchange=exchange, contract=contract, price=price, now_date=now_date)
                # 平多开空
                elif target_num[contract] < 0:
                    self._close(exchange=exchange, contract=contract, price=price, now_date=now_date)
                    self._open(exchange=exchange, contract=contract, num=target_num[contract], price=price,
                               now_date=now_date)
            # 持有空头
            elif hold_num < 0:
                # 加空
                if target_num[contract] < hold_num:
                    self._inc(exchange=exchange, contract=contract, num=target_num[contract] - hold_num, price=price,
                              now_date=now_date)
                # 减空
                elif (target_num[contract] > hold_num) & (target_num[contract] < 0):
                    self._dec(exchange=exchange, contract=contract, num=target_num[contract] - hold_num, price=price,
                              now_date=now_date)
                # 平空
                elif target_num[contract] == 0:
                    self._close(exchange=exchange, contract=contract, price=price, now_date=now_date)
                # 平空开多
                elif target_num[contract] > 0:
                    self._close(exchange=exchange, contract=contract, price=price, now_date=now_date)
                    self._open(exchange=exchange, contract=contract, num=target_num[contract], price=price,
                               now_date=now_date)
