import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test_hf import HFVolumeRatioFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_volume_ratio(begin_date='2011-01-01', end_date='2021-02-28'):

    cal_factor = HFVolumeRatioFactor(
        factor_name='hf_rtn%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        # contract_list=[x for x in NORMAL_CONTRACT_INFO if x['id'] == 'SA'],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    v5_v20 = pd.concat(cal_factor.v5_v20)
    v5_v30 = pd.concat(cal_factor.v5_v30)
    v10_v30 = pd.concat(cal_factor.v10_v30)
    std5_std20 = pd.concat(cal_factor.std5_std20)
    std5_std30 = pd.concat(cal_factor.std5_std30)
    std10_std30 = pd.concat(cal_factor.std10_std30)

    v5_v20.reset_index(drop=True, inplace=True)
    v5_v30.reset_index(drop=True, inplace=True)
    v10_v30.reset_index(drop=True, inplace=True)
    std5_std20.reset_index(drop=True, inplace=True)
    std5_std30.reset_index(drop=True, inplace=True)
    std10_std30.reset_index(drop=True, inplace=True)

    v5_v20.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tv5_v20.csv'))
    v5_v30.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tv5_v30.csv'))
    v10_v30.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tv10_v30.csv'))
    std5_std20.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tstd5_std20.csv'))
    std5_std30.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tstd5_std30.csv'))
    std10_std30.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tstd10_std30.csv'))

if __name__ == '__main__':
    hf_volume_ratio()
