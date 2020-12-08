import pandas as pd
from utils.base_para import *

pd.set_option('expand_frame_repr', False)

class _ContractSeries:
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


class Contract:
    def __init__(self, contract_name, month_list):
        self.operate_contract = ''
        self.contract_name = contract_name
        self.month_list = month_list
        self._contract_series = _ContractSeries(
            contract_name=contract_name,
            month_list=month_list
        )
        self.contract_volume = self._fetch_volume()

    def _fetch_volume(self):
        sql = 'select * from "%s"."%s_volume"' % (self.contract_name, self.contract_name)
        return pd.read_sql_query(sql, con=eg)

    def now_main_contract(self, now_date):
        """
        找当前主力合约
        :param now_date:
        :return:
        """
        # now_date = pd.to_datetime(now_date)
        volume_data = self.contract_volume.loc[self.contract_volume['datetime'] == now_date].dropna(axis=1)
        volume_data = volume_data[volume_data.columns[2:]].T.reset_index()

        volume_data.sort_values(by=volume_data.columns[1], inplace=True, ascending=False)
        return volume_data['index'].iloc[0]

    def renew_operate_contract(self, now_contract, now_date):
        """
        根据下述规则更新操作合约:
            1.交割日期更远
            2.成交量更大
        :param now_contract:
        :param now_date:
        :return:
        """
        main_contract = self.now_main_contract(now_date=now_date)
        # hist_contract = [now_contract]
        further_contract = [now_contract]
        for i in range(len(self.month_list)):
            # hist_contract.append(self._contract_series.last_contract(now_contract=hist_contract[-1]))
            further_contract.append(self._contract_series.next_contract(now_contract=further_contract[-1]))
        if main_contract in further_contract:
            return main_contract
        else:
            return now_contract


if __name__ == '__main__':
    m_contract = Contract(
        contract_name='M',
        month_list=[1, 3, 5, 7, 8, 9, 11, 12]
    )
    new_contract = m_contract.renew_operate_contract(now_contract='M1905', now_date='2019-11-25')
    print(new_contract)
