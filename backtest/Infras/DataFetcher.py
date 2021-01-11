from utils.base_para import *
import pandas as pd
pd.set_option('expand_frame_repr', False)


class DataFetcher:
    def __init__(self, database):
        self._eg = database

    def get_contract_data(self, contract):
        sql = 'select * from "%s"."%s"' % (contract[:-4], contract)
        data = pd.read_sql_query(sql, con=self._eg)
        data['trading_date'] = pd.to_datetime(data['trading_date'])
        data['datetime'] = pd.to_datetime(data['datetime'])
        return data

    def get_contract_data_hf(self, contract):
        sql = 'select * from "%s_1m"."%s"' % (contract[:-4], contract)
        data = pd.read_sql_query(sql, con=self._eg)
        data['trading_date'] = pd.to_datetime(data['trading_date'])
        data['datetime'] = pd.to_datetime(data['datetime'])
        return data

    def get_contract_data_list(self, commodity):
        sql = 'select tablename from pg_tables where schemaname=\'%s\'' % commodity
        data = pd.read_sql_query(sql, con=self._eg)
        return list(data['tablename'])

if __name__ == '__main__':
    data_fetcher = DataFetcher(database=eg)
    data = data_fetcher.get_contract_data('M2105')
    print(data)
