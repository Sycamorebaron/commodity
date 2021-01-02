import pandas as pd
from backtest.Infras.DataFetcher import DataFetcher
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
    def __init__(self, contract_name, month_list, init_margin_rate, contract_unit, open_comm, close_comm):
        self.operate_contract = ''
        self.data_dict = {}
        self.data_fetcher = DataFetcher(database=eg)
        self.contract_name = contract_name
        self.month_list = month_list
        self._contract_series = _ContractSeries(
            contract_name=contract_name,
            month_list=month_list
        )
        self.contract_volume = self._fetch_volume()
        self.init_margin_rate = init_margin_rate
        self.contract_unit = contract_unit
        self.open_comm = open_comm
        self.close_comm = close_comm

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

    def renew_operate_contract(self, now_date):
        """
        根据下述规则更新操作合约:
            1.交割日期更远
            2.成交量更大
        :param now_contract:
        :param now_date:
        :return:
        """
        main_contract = self.now_main_contract(now_date=now_date)
        if self.operate_contract != '':
            further_contract = [self.operate_contract]
            for _ in range(len(self.month_list)):
                further_contract.append(self._contract_series.next_contract(now_contract=further_contract[-1]))
            if main_contract in further_contract:
                self.operate_contract = main_contract
        else:
            self.operate_contract = main_contract

    def now_open_contract(self, now_date):
        volume_data = self.contract_volume.loc[self.contract_volume['datetime'] == now_date].dropna(axis=1)
        volume_data = volume_data[volume_data.columns[2:]].T.reset_index()
        return list(volume_data['index'])

    def renew_open_contract(self, now_date):
        """
        更新当前开放的合约
        :param now_date:
        :return:
        """

        now_open_contract = self.now_open_contract(now_date=now_date)
        for contract in now_open_contract:
            if contract not in self.data_dict.keys():
                self.data_dict[contract] = self.data_fetcher.get_contract_data(contract=contract)

        _now_ky = list(self.data_dict.keys())
        for contract in _now_ky:
            if contract not in now_open_contract:
                self.data_dict.pop(contract)

    def get_contract_data(self, contract, now_date):
        try:
            data = self.data_dict[contract]
        except Exception as e:
            print(e)
            raise Exception('Contract.get_contract_data ERROR: CONTRACT NOT IN DATA DICT')
        data = data.loc[data['trading_date'] == now_date]
        return data['close'].iloc[-1]
