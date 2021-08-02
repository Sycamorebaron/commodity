import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_factor.factor_test_hf import HFUpDownFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_up_down(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFUpDownFactor(
        factor_name='hf_rtn%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    up_rtn_mean = pd.concat(cal_factor.up_rtn_mean)
    up_rtn_std = pd.concat(cal_factor.up_rtn_std)
    up_move_vol_pct = pd.concat(cal_factor.up_move_vol_pct)
    up_vol_pct = pd.concat(cal_factor.up_vol_pct)
    down_rtn_mean = pd.concat(cal_factor.down_rtn_mean)
    down_rtn_std = pd.concat(cal_factor.down_rtn_std)
    down_move_vol_pct = pd.concat(cal_factor.down_move_vol_pct)
    down_vol_pct = pd.concat(cal_factor.down_vol_pct)
    trend_ratio = pd.concat(cal_factor.trend_ratio)

    up_rtn_mean.reset_index(drop=True, inplace=True)
    up_rtn_std.reset_index(drop=True, inplace=True)
    up_move_vol_pct.reset_index(drop=True, inplace=True)
    up_vol_pct.reset_index(drop=True, inplace=True)
    down_rtn_mean.reset_index(drop=True, inplace=True)
    down_rtn_std.reset_index(drop=True, inplace=True)
    down_move_vol_pct.reset_index(drop=True, inplace=True)
    down_vol_pct.reset_index(drop=True, inplace=True)
    trend_ratio.reset_index(drop=True, inplace=True)

    up_rtn_mean.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tup_rtn_mean.csv'))
    up_rtn_std.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tup_rtn_std.csv'))
    up_move_vol_pct.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tup_move_vol_pct.csv'))
    up_vol_pct.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tup_vol_pct.csv'))
    down_rtn_mean.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tdown_rtn_mean.csv'))
    down_rtn_std.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tdown_rtn_std.csv'))
    down_move_vol_pct.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tdown_move_vol_pct.csv'))
    down_vol_pct.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tdown_vol_pct.csv'))
    trend_ratio.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Ttrend_ratio.csv'))

if __name__ == '__main__':
    hf_up_down()

