import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_daily_factor_1D.factor_test_daily1T import HFUpDownFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_updown_factor(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFUpDownFactor(
        factor_name='hf_up_down_factor_%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] == 'SA'],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    up_rtn_mean = pd.concat(cal_factor.up_rtn_mean).reset_index(drop=True)
    up_rtn_std = pd.concat(cal_factor.up_rtn_std).reset_index(drop=True)
    up_move_vol_pct = pd.concat(cal_factor.up_move_vol_pct).reset_index(drop=True)
    up_vol_pct = pd.concat(cal_factor.up_vol_pct).reset_index(drop=True)

    down_rtn_mean = pd.concat(cal_factor.down_rtn_mean).reset_index(drop=True)
    down_rtn_std = pd.concat(cal_factor.down_rtn_std).reset_index(drop=True)
    down_move_vol_pct = pd.concat(cal_factor.down_move_vol_pct).reset_index(drop=True)
    down_vol_pct = pd.concat(cal_factor.down_vol_pct).reset_index(drop=True)

    trend_ratio = pd.concat(cal_factor.trend_ratio).reset_index(drop=True)

    up_rtn_mean.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dup_rtn_mean.csv'))
    up_rtn_std.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dup_rtn_mean.csv'))
    up_move_vol_pct.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dup_move_vol_pct.csv'))
    up_vol_pct.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dup_vol_pct.csv'))

    down_rtn_mean.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1ddown_rtn_mean.csv'))
    down_rtn_std.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1ddown_rtn_std.csv'))
    down_move_vol_pct.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1ddown_move_vol_pct.csv'))
    down_vol_pct.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1ddown_vol_pct.csv'))

    trend_ratio.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dtrend_ratio.csv'))


if __name__ == '__main__':
    hf_updown_factor('2011-01-01', '2021-02-28')
