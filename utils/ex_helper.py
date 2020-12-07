
class FutureContract:
    def __init__(self, contract_name, month_list):
        self._month_list = self._gen_month(month_list)
        self.contract_name = contract_name

    @staticmethod
    def _gen_month(month_list):
        return ['0%s' % i for i in month_list if i < 10] + [str(i) for i in month_list if i > 10]

    @staticmethod
    def _next_year(this_year):
        this_year = int(this_year)
        if this_year + 1 < 10:
            return '0' + str(this_year + 1)
        else:
            return str(this_year + 1)

    @staticmethod
    def _last_year(this_year):
        this_year = int(this_year)
        if this_year - 1 < 10:
            return '0' + str(this_year - 1)
        else:
            return str(this_year - 1)

    def _next_month(self, now_month):
        if now_month not in self._month_list:
            raise Exception('now month not in month list')
        if now_month != self._month_list[-1]:
            return self._month_list[self._month_list.index(now_month) + 1]
        else:
            return self._month_list[0]

    def _last_month(self, now_month):
        if now_month not in self._month_list:
            raise Exception('now month not in month list')
        if now_month != self._month_list[0]:
            return self._month_list[self._month_list.index(now_month) - 1]
        else:
            return self._month_list[-1]

    def next_contract(self, now_contract):
        if now_contract[-2:] not in self._month_list:
            raise Exception('wrong contract input')
        if now_contract[-2:] != self._month_list[-1]:
            return now_contract[:-2] + self._next_month(now_contract[-2:])

        else:
            return '%s%s%s' % (
                self.contract_name, self._next_year(now_contract[-4: -2]), self._month_list[0]
            )

    def last_contract(self, now_contract):
        if now_contract[-2:] not in self._month_list:
            raise Exception('wrong contract input')
        if now_contract[-2:] != self._month_list[0]:
            return now_contract[:-2] + self._last_month(now_contract[-2:])
        else:
            return '%s%s%s' % (
                self.contract_name, self._last_year(now_contract[-4: -2]), self._month_list[-1]
            )
