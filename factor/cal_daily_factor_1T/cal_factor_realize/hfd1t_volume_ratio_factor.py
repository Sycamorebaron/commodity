import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_daily_factor_1T.factor_test_daily1T import HFVolumeRatioFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_volume_ratio_factor(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFVolumeRatioFactor(
        factor_name='hf_big_factor_%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] in ['L', 'C', 'M']],
        # contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )

    cal_factor.test()

    open_5t_pct = pd.concat(cal_factor.open_5t_pct).reset_index(drop=True)
    open_15t_pct = pd.concat(cal_factor.open_15t_pct).reset_index(drop=True)
    open_30t_pct = pd.concat(cal_factor.open_30t_pct).reset_index(drop=True)
    close_5t_pct = pd.concat(cal_factor.close_5t_pct).reset_index(drop=True)
    close_15t_pct = pd.concat(cal_factor.close_15t_pct).reset_index(drop=True)
    close_30t_pct = pd.concat(cal_factor.close_30t_pct).reset_index(drop=True)

    open_5t_pct.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dopen_5t_pct.csv'))
    open_15t_pct.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dopen_15t_pct.csv'))
    open_30t_pct.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dopen_30t_pct.csv'))
    close_5t_pct.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dclose_5t_pct.csv'))
    close_15t_pct.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dclose_15t_pct.csv'))
    close_30t_pct.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dclose_30t_pct.csv'))


if __name__ == '__main__':
    hf_volume_ratio_factor('2011-01-01', '2021-02-28')
