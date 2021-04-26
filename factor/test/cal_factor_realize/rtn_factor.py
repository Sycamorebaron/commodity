import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test import RtnFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH


pd.set_option('expand_frame_repr', False)


def rtn_factor_cal(begin_date='2010-01-04', end_date='2021-02-28'):
    cal_factor = RtnFactor(
        factor_name='moment',
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()

    l_first_5t = pd.DataFrame(cal_factor.first_5T_rtn)
    l_first_10t = pd.DataFrame(cal_factor.first_10T_rtn)
    l_first_30t = pd.DataFrame(cal_factor.first_30T_rtn)
    l_last_5t = pd.DataFrame(cal_factor.last_5T_rtn)
    l_last_10t = pd.DataFrame(cal_factor.last_10T_rtn)
    l_last_30t = pd.DataFrame(cal_factor.last_30T_rtn)

    l_first_5t.to_excel(os.path.join(OUTPUT_DATA_PATH, 'first_5t.xlsx'))
    l_first_10t.to_excel(os.path.join(OUTPUT_DATA_PATH, 'first_10t.xlsx'))
    l_first_30t.to_excel(os.path.join(OUTPUT_DATA_PATH, 'first_30t.xlsx'))

    l_last_5t.to_excel(os.path.join(OUTPUT_DATA_PATH, 'last_5t.xlsx'))
    l_last_10t.to_excel(os.path.join(OUTPUT_DATA_PATH, 'last_10t.xlsx'))
    l_last_30t.to_excel(os.path.join(OUTPUT_DATA_PATH, 'last_30t.xlsx'))


if __name__ == '__main__':
    rtn_factor_cal()
