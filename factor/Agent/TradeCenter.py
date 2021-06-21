import string


class TradeCenter:

    @staticmethod
    def _open(exchange, contract, num, price, now_dt):
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
        # print('OPEN', now_dt, contract, num, price)
        exchange.account.cash -= (
                open_margin + abs(num) * exchange.contract_dict[commodity].open_comm * price *
                exchange.contract_dict[commodity].contract_unit
        )

        exchange.account.position.holding_position[commodity][contract] = {
            'open_date': now_dt,
            'use_margin': open_margin,
            'open_price': price,  # 开仓均价
            'hold_price': price,  # 每日结算持仓均价
            'num': num,
            'pnl': 0,
        }

    @staticmethod
    def _close(exchange, contract, price, now_dt):
        """
        纯平，平掉某个合约所有仓位，equity和cash减掉平仓手续费，去掉position，计算盈亏，风险度在最外层更新
        :param exchange:
        :param price:
        :return:
        """
        commodity = contract.strip('0123456789')
        num = exchange.account.position.holding_position[commodity][contract]['num']
        use_margin = exchange.account.position.holding_position[commodity][contract]['use_margin']
        today_profit = \
            (price - exchange.account.position.holding_position[commodity][contract]['hold_price']) * num * \
            exchange.contract_dict[commodity].contract_unit
        # print('CLOSE', now_dt, contract, num, price)
        exchange.account.cash += (
            today_profit + use_margin - abs(num) * exchange.contract_dict[commodity].close_comm * price *
            exchange.contract_dict[commodity].contract_unit
        )

        exchange.account.position.drop(contract=contract)

    @staticmethod
    def _inc(exchange, contract, num, price, now_dt):
        """
        加仓，含加多和加空
        :param exchange:
        :param num:
        :param price:
        :return:
        """
        commodity = contract.strip('0123456789')
        holding_num = exchange.account.position.holding_position[commodity][contract]['num']
        hold_price = exchange.account.position.holding_position[commodity][contract]['hold_price']
        now_pnl = exchange.account.position.holding_position[commodity][contract]['pnl']
        using_margin = exchange.account.position.holding_position[commodity][contract]['use_margin']

        avg_price = (holding_num * hold_price + num * price) / (holding_num + num)

        open_margin = \
            exchange.contract_dict[commodity].contract_unit * \
            exchange.contract_dict[commodity].init_margin_rate * price * abs(num)
        print('INC', now_dt, contract, num, price)
        exchange.account.cash -= (
                open_margin + abs(num) * exchange.contract_dict[commodity].open_comm
        )

        exchange.account.position.holding_position[commodity][contract] = {
            'open_date': now_dt,
            'use_margin': open_margin + using_margin,
            'open_price': avg_price,  # 开仓均价
            'hold_price': avg_price,  # 每日结算持仓均价
            'num': holding_num + num,
            'pnl': now_pnl,
        }

    @staticmethod
    def _dec(exchange, contract, num, price, now_dt):
        """
        减仓，含减多和减空
        :param exchange:
        :param num:
        :param price:
        :return:
        """
        commodity = contract.strip('0123456789')
        holding_num = exchange.account.position.holding_position[commodity][contract]['num']

        # 使用当前平仓价格（最新价）更新占用保证金数量和浮动盈亏
        # latest_use_margin = price * exchange.contract_dict[commodity].contract_unit * exchange.contract_dict[commodity].init_margin_rate * holding_num
        latest_pnl = \
            (price - exchange.account.position.holding_position[commodity][contract]['hold_price']) * holding_num * \
            exchange.contract_dict[commodity].contract_unit
        # exchange.account.position.holding_position[commodity][contract]['use_margin'] = latest_use_margin
        exchange.account.position.holding_position[commodity][contract]['pnl'] = latest_pnl

        release_margin = \
            exchange.account.position.holding_position[commodity][contract]['use_margin'] * (abs(num) / holding_num)
        release_pnl = latest_pnl * abs(num / holding_num)

        exchange.account.cash += (
                release_pnl + release_margin - abs(num) * exchange.contract_dict[commodity].open_comm
        )

        # 注意正负号！多头减仓num为负数，空头减仓num为正数
        exchange.account.position.holding_position[commodity][contract]['use_margin'] -= release_margin
        exchange.account.position.holding_position[commodity][contract]['pnl'] -= release_pnl
        exchange.account.position.holding_position[commodity][contract]['num'] += num
        print('trade_center.dec', latest_pnl, release_pnl)
        print('trade_center.dec', exchange.account.position.holding_position[commodity][contract], exchange.account.cash)

    def trade(self, exchange, target_num, now_dt, field):

        trade_info = []
        for contract in target_num.keys():
            if contract in exchange.account.position.holding_position[contract.strip('1234567890')].keys():
                hold_num = exchange.account.position.holding_position[contract.strip('1234567890')][contract]['num']
            else:
                hold_num = 0
            price = exchange.contract_dict[contract.rstrip(string.digits)]._get_contract_data(contract, now_dt, field)
            # 无持仓
            if hold_num == 0:
                # 开多
                if target_num[contract] > 0:
                    self._open(exchange=exchange, contract=contract, num=target_num[contract], price=price,
                               now_dt=now_dt)
                    trade_info.append(
                        {'now_date': now_dt, 'contract': contract, 'trade_type': 'long_open',
                         'num': target_num[contract], 'price': price}
                    )
                # 开空
                elif target_num[contract] < 0:
                    self._open(exchange=exchange, contract=contract, num=target_num[contract], price=price,
                               now_dt=now_dt)
                    trade_info.append(
                        {'now_date': now_dt, 'contract': contract, 'trade_type': 'short_open',
                         'num': target_num[contract], 'price': price}
                    )
            # 持有多头
            elif hold_num > 0:
                # 加多
                if target_num[contract] > hold_num:
                    self._inc(exchange=exchange, contract=contract, num=target_num[contract] - hold_num, price=price,
                              now_dt=now_dt)
                    trade_info.append(
                        {'now_date': now_dt, 'contract': contract, 'trade_type': 'long_inc',
                         'num': target_num[contract] - hold_num, 'price': price}
                    )
                # 减多
                elif (target_num[contract] < hold_num) & (target_num[contract] > 0):
                    self._dec(exchange=exchange, contract=contract, num=target_num[contract] - hold_num, price=price,
                              now_dt=now_dt)
                    trade_info.append(
                        {'now_date': now_dt, 'contract': contract, 'trade_type': 'long_dec',
                         'num': target_num[contract] - hold_num, 'price': price}
                    )
                # 平多
                elif target_num[contract] == 0:
                    self._close(exchange=exchange, contract=contract, price=price, now_dt=now_dt)
                    trade_info.append(
                        {'now_date': now_dt, 'contract': contract, 'trade_type': 'long_close', 'num': -hold_num,
                         'price': price}
                    )
                # 平多开空
                elif target_num[contract] < 0:
                    self._close(exchange=exchange, contract=contract, price=price, now_dt=now_dt)
                    self._open(exchange=exchange, contract=contract, num=target_num[contract], price=price,
                               now_dt=now_dt)
                    trade_info.append(
                        {'now_date': now_dt, 'contract': contract, 'trade_type': 'long_close_short_open',
                         'num': target_num[contract] - hold_num, 'price': price}
                    )
            # 持有空头
            elif hold_num < 0:
                # 加空
                if target_num[contract] < hold_num:
                    self._inc(exchange=exchange, contract=contract, num=target_num[contract] - hold_num, price=price,
                              now_dt=now_dt)
                    trade_info.append(
                        {'now_date': now_dt, 'contract': contract, 'trade_type': 'short_inc',
                         'num': target_num[contract] - hold_num, 'price': price}
                    )
                # 减空
                elif (target_num[contract] > hold_num) & (target_num[contract] < 0):
                    self._dec(exchange=exchange, contract=contract, num=target_num[contract] - hold_num, price=price,
                              now_dt=now_dt)
                    trade_info.append(
                        {'now_date': now_dt, 'contract': contract, 'trade_type': 'short_dec',
                         'num': target_num[contract] - hold_num, 'price': price}
                    )
                # 平空
                elif target_num[contract] == 0:
                    self._close(exchange=exchange, contract=contract, price=price, now_dt=now_dt)
                    trade_info.append(
                        {'now_date': now_dt, 'contract': contract, 'trade_type': 'short_close',
                         'num': target_num[contract] - hold_num, 'price': price}
                    )
                # 平空开多
                elif target_num[contract] > 0:
                    self._close(exchange=exchange, contract=contract, price=price, now_dt=now_dt)
                    self._open(exchange=exchange, contract=contract, num=target_num[contract], price=price,
                               now_dt=now_dt)
                    trade_info.append(
                        {'now_date': now_dt, 'contract': contract, 'trade_type': 'short_close_long_open',
                         'num': target_num[contract] - hold_num, 'price': price}
                    )

        return trade_info
