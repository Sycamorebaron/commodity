import sys
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from utils.base_para import *


class CommExpRtn:
    def __init__(self, comm, model, begin_date, end_date, train_data_len, forecast_rtn, use_factor_list):
        self.comm = comm
        self.model = self._gen_model(model=model)
        self.begin_date = pd.to_datetime(begin_date)
        self.end_date = pd.to_datetime(end_date)
        self.train_data_len = train_data_len
        self.f_rtn = self._gen_f_rtn(forecast_rtn)
        self.use_factor_list = use_factor_list

    def _gen_model(self, model):
        pass

    def _gen_f_rtn(self, forecast_rtn):
        pass

    def report(self):
        pass
