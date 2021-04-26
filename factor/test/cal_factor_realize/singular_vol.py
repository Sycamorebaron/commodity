import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test import SingularVol
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path_5T, OUTPUT_DATA_PATH


pd.set_option('expand_frame_repr', False)


def singular_vol_cal(begin_date='2010-01-04', end_date='2021-02-28'):
    cal_factor = SingularVol(
        factor_name='moment',
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path_5T
    )
    cal_factor.test()

    l_BV = pd.DataFrame(cal_factor.BV)
    l_BV_sigma = pd.DataFrame(cal_factor.BV_sigma)
    l_bollerslev_RSJ = pd.DataFrame(cal_factor.bollerslev_RSJ)

    l_BV.to_excel(os.path.join(OUTPUT_DATA_PATH, 'BV.xlsx'))
    l_BV_sigma.to_excel(os.path.join(OUTPUT_DATA_PATH, 'BV_sigma.xlsx'))
    l_bollerslev_RSJ.to_excel(os.path.join(OUTPUT_DATA_PATH, 'bollerslev_RSJ.xlsx'))


if __name__ == '__main__':

    singular_vol_cal()
