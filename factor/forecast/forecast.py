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
    _comm = 'FG'
    forecast = Forecast(
        comm=_comm,
        target='main_day_rtn',
        rtn_data_path=OUTPUT_DATA_PATH,
        factor_data_path=OUTPUT_DATA_PATH,
        factor_list=['first_5t', 'first_10t', 'first_30t', 'last_5t', 'last_10t', 'last_30t']
    )
    forecast.forecast(algo='ols')
    forecast.dataset.to_excel('test_res.xlsx')
    # forecast.feature_eng.dataset.to_excel('test_res.xlsx')


