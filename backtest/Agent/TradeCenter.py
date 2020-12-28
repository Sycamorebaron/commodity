import string


class TradeCenter:

    def _open(self, exchange, num, price):
        """
        纯开
        :param exchange:
        :param num:
        :param price:
        :return:
        """
        pass

    def _close(self, exchange, price):
        """
        纯平
        :param exchange:
        :param price:
        :return:
        """
        pass

    def _inc(self, exchange, num, price):
        """
        加仓，含加多和加空
        :param exchange:
        :param num:
        :param price:
        :return:
        """
        pass

    def _dec(self, exchange, num, price):
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
                    self._open(exchange=exchange, num=target_num[contract], price=price)
                # 开空
                elif target_num[contract] < 0:
                    self._open(exchange=exchange, num=target_num[contract], price=price)
            # 持有多头
            elif hold_num > 0:
                # 加多
                if target_num[contract] > hold_num:
                    self._inc(exchange=exchange, num=target_num[contract] - hold_num, price=price)
                # 减多
                elif (target_num[contract] < hold_num) & (target_num[contract] > 0):
                    self._dec(exchange=exchange, num=target_num[contract] - hold_num, price=price)
                # 平多
                elif target_num[contract] == 0:
                    self._close(exchange=exchange, price=price)
                # 平多开空
                elif target_num[contract] < 0:
                    self._close(exchange=exchange, price=price)
                    self._open(exchange=exchange, num=target_num[contract], price=price)
            # 持有空头
            elif hold_num < 0:
                # 加空
                if target_num[contract] < hold_num:
                    self._inc(exchange=exchange, num=target_num[contract] - hold_num, price=price)
                # 减空
                elif (target_num[contract] > hold_num) & (target_num[contract] < 0):
                    self._dec(exchange=exchange, num=target_num[contract] - hold_num, price=price)
                # 平空
                elif target_num[contract] == 0:
                    self._close(exchange=exchange, price=price)
                # 平空开多
                elif target_num[contract] > 0:
                    self._close(exchange=exchange, price=price)
                    self._open(exchange=exchange, num=target_num[contract], price=price)
