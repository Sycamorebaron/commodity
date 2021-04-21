import os
import pandas as pd


class ExcelDataFetcher:
    def __init__(self, local_data_path):
        self.local_data_path = local_data_path

    def get_contract_data(self, contract):
        commodity = contract.strip('1234567890')

        data = pd.read_csv(os.path.join(self.local_data_path, commodity, '%s.csv' % contract))

        data = data[[
            'order_book_id', 'datetime', 'open', 'high', 'low', 'close', 'volume', 'open_interest', 'total_turnover'
        ]].copy()
        data['datetime'] = pd.to_datetime(data['datetime'])

        return data

    def get_data(self, dirname, file):
        data = pd.read_csv(os.path.join(self.local_data_path, dirname, '%s.csv' % file))

        return data



    def get_contract_data_list(self, commodity):
        files = []
        for roots, dirs, files in os.walk(os.path.join(self.local_data_path, commodity)):
            if files:
                break
        files = [i[:-4] for i in files]
        return files

    def save_data(self, data, dirname, filename):

        data.to_csv(os.path.join(self.local_data_path, dirname, '%s.csv' % filename))


