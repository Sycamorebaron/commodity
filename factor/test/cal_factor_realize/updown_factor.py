import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test import UpDownFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH


pd.set_option('expand_frame_repr', False)


def updown_factor_cal():
    cal_factor = UpDownFactor(
        factor_name='moment',
        begin_date='2018-01-01',
        end_date='2021-02-28',
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()

    l_up_rtn_var = pd.DataFrame(cal_factor.up_rtn_var)
    l_down_rtn_var = pd.DataFrame(cal_factor.down_rtn_var)
    l_up_vol_pct = pd.DataFrame(cal_factor.up_vol_pct)
    l_up_amt_pct = pd.DataFrame(cal_factor.up_amt_pct)
    l_trend_ratio = pd.DataFrame(cal_factor.trend_ratio)

    l_up_rtn_var.to_excel(os.path.join(OUTPUT_DATA_PATH, 'up_rtn_var.xlsx'))
    l_down_rtn_var.to_excel(os.path.join(OUTPUT_DATA_PATH, 'down_rtn_var.xlsx'))
    l_up_vol_pct.to_excel(os.path.join(OUTPUT_DATA_PATH, 'up_vol_pct.xlsx'))
    l_up_amt_pct.to_excel(os.path.join(OUTPUT_DATA_PATH, 'up_amt_pct.xlsx'))
    l_trend_ratio.to_excel(os.path.join(OUTPUT_DATA_PATH, 'trend_ratio.xlsx'))


if __name__ == '__main__':

    updown_factor_cal()
