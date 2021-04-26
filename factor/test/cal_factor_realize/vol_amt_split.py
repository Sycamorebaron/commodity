import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test import VolAmtSplit
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path_5T, OUTPUT_DATA_PATH


pd.set_option('expand_frame_repr', False)


class _VolAmtSplit(VolAmtSplit):
    def trunc_data(self, _data):
        return VolAmtSplit._trunc_data(self, _data)


def vol_amt_split_cal(begin_date='2010-01-04', end_date='2021-02-28'):
    cal_factor = VolAmtSplit(
        factor_name='moment',
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path_5T
    )
    cal_factor.test()

    l_morning_vol_pct = pd.DataFrame(cal_factor.morning_vol_pct)
    l_down_vol_pct = pd.DataFrame(cal_factor.down_vol_pct)
    l_open_30t_vol_pct = pd.DataFrame(cal_factor.open_30t_vol_pct)
    l_last_30t_vol_pct = pd.DataFrame(cal_factor.last_30t_vol_pct)
    l_morning_amt_pct = pd.DataFrame(cal_factor.morning_amt_pct)
    l_down_amt_pct = pd.DataFrame(cal_factor.down_amt_pct)
    l_open_30t_amt_pct = pd.DataFrame(cal_factor.open_30t_amt_pct)
    l_last_30t_amt_pct = pd.DataFrame(cal_factor.last_30t_amt_pct)

    l_morning_vol_pct.to_excel(os.path.join(OUTPUT_DATA_PATH, 'morning_vol_pct.xlsx'))
    l_down_vol_pct.to_excel(os.path.join(OUTPUT_DATA_PATH, 'down_vol_pct.xlsx'))
    l_open_30t_vol_pct.to_excel(os.path.join(OUTPUT_DATA_PATH, 'open_30t_vol_pct.xlsx'))
    l_last_30t_vol_pct.to_excel(os.path.join(OUTPUT_DATA_PATH, 'last_30t_vol_pct.xlsx'))
    l_morning_amt_pct.to_excel(os.path.join(OUTPUT_DATA_PATH, 'morning_amt_pct.xlsx'))
    l_down_amt_pct.to_excel(os.path.join(OUTPUT_DATA_PATH, 'down_amt_pct.xlsx'))
    l_open_30t_amt_pct.to_excel(os.path.join(OUTPUT_DATA_PATH, 'open_30t_amt_pct.xlsx'))
    l_last_30t_amt_pct.to_excel(os.path.join(OUTPUT_DATA_PATH, 'last_30t_amt_pct.xlsx'))



def _vol_amt_split_cal(begin_date='2010-01-04', end_date='2021-02-28'):
    cal_factor = _VolAmtSplit(
        factor_name='moment',
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path_5T
    )
    cal_factor.test()

    l_down_vol_pct = pd.DataFrame(cal_factor.down_vol_pct)
    l_down_amt_pct = pd.DataFrame(cal_factor.down_amt_pct)

    l_down_vol_pct.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_down_vol_pct.xlsx'))
    l_down_amt_pct.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_down_amt_pct.xlsx'))



if __name__ == '__main__':
    vol_amt_split_cal()