import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.forecast.algo import Algo
from factor.forecast.feature_eng import FeatureEng
from utils.base_para import OUTPUT_DATA_PATH



class Forecast:
    def __init__(self, comm, target, rtn_data_path, factor_data_path, factor_list):
        self.algo = Algo()
        self.feature_eng = FeatureEng(
            comm=comm, target=target, rtn_data_path=rtn_data_path, factor_data_path=factor_data_path,
            factor_list=factor_list
        )
        self.dataset = self.feature_eng.dataset

    def forecast(self, algo, **kwargs):
        algo_str = \
            'self.algo.%s(self.dataset[self.feature_eng.factor_list], self.dataset[self.feature_eng.target], **kwargs)' \
            % algo

        self.dataset['fitted_rtn'] = eval(algo_str)


if __name__ == '__main__':
    factor_list = []
    for roots, dirs, files in os.walk(r'C:\futures_factor'):
        if files:
            factor_list = [i[:-5] for i in files]

    fg_forecast = Forecast(
        comm='FG',
        target='main_day_rtn',
        rtn_data_path=OUTPUT_DATA_PATH,
        factor_data_path=r'C:\futures_factor',
        factor_list=factor_list
    )
    fg_forecast.dataset.to_excel(os.path.join(OUTPUT_DATA_PATH, 'fg_test_data.xlsx'))
    exit()
    fg_forecast.forecast(algo='ols')
    fg_forecast.dataset.to_excel('test_res.xlsx')


