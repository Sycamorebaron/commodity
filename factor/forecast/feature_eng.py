import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from utils.base_para import OUTPUT_DATA_PATH
pd.set_option('expand_frame_repr', False)


class FeatureEng:
    def __init__(self, comm, target, rtn_data_path, factor_data_path, factor_list):
        self.comm = comm
        self.rtn_data = pd.read_excel(os.path.join(rtn_data_path, 'daily_rtn.xlsx'))[[
            'date', '%s_%s' % (comm, target)]].copy()
        self.rtn_data.columns = ['date', 'rtn']
        self.factor = self._gen_factor(factor_list=factor_list, factor_path=factor_data_path)
        self.dataset = self._gen_dataset()
        self.target = 'f_rtn'  # 供调用的数据集标签
        self.factor_list = factor_list  # 供调用的数据集标签

    def _gen_dataset(self):
        dataset = self.rtn_data.merge(self.factor, on='date', how='outer')
        dataset.dropna(subset=['rtn'], inplace=True, axis=0)
        dataset.reset_index(drop=True, inplace=True)
        dataset['f_rtn'] = dataset['rtn'].shift(-1)
        print(dataset)
        # dataset.dropna(how='all', axis=0, inplace=True)
        return dataset

    def _gen_factor(self, factor_list, factor_path):

        sum_factor_data = pd.DataFrame()
        for factor in factor_list:
            print(factor)
            factor_data = pd.read_excel(os.path.join(factor_path, '%s.xlsx' % factor))[['date', self.comm]].copy()
            factor_data.columns = ['date', factor]
            if len(sum_factor_data):
                sum_factor_data = sum_factor_data.merge(factor_data, on='date', how='outer')
            else:
                sum_factor_data = factor_data
        return sum_factor_data



if __name__ == '__main__':

    fg_forecast = FeatureEng(
        comm='FG',
        target='main_day_rtn',
        rtn_data_path=OUTPUT_DATA_PATH,
        factor_data_path=r'C:\futures_factor',
        factor_list=['first_5t', 'first_10t', 'first_30t', 'last_5t', 'last_10t', 'last_30t']
    )
    fg_forecast.dataset.to_excel(os.path.join(OUTPUT_DATA_PATH, '%s.xlsx' % fg_forecast.comm))
