from utils.base_para import *
import pandas as pd
import os
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

class ExcelDataFetcher:
    def __init__(self, data_path):
        self.data_path = data_path

    def get_contract_data_hf(self, contract):
        d_path = os.path.join(self.data_path, '%s.csv' % contract)
        data = pd.read_csv(d_path)
        data['trading_date'] = pd.to_datetime(data['trading_date'])
        data['datetime'] = pd.to_datetime(data['datetime'])
        return data

    def get_contract_data_list(self, commodity):
        local_files = []
        for roots, firs, files in os.walk(self.data_path):
            if files:
                local_files = files

        comm_list = [i for i in local_files if i[:-4].strip('1234567890') == commodity]
        return comm_list


if __name__ == '__main__':
    data_fetcher = DataFetcher(database=eg)
    data = data_fetcher.get_contract_data('M2105')
    print(data)
