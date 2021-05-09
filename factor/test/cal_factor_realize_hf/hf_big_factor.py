import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test_hf import HFBigFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_big_factor(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFBigFactor(
        factor_name='hf_rtn%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    vbig_rtn_mean = pd.concat(cal_factor.vbig_rtn_mean)
    vbig_rtn_vol = pd.concat(cal_factor.vbig_rtn_vol)
    vbig_rv_corr = pd.concat(cal_factor.vbig_rv_corr)
    abig_rtn_mean = pd.concat(cal_factor.abig_rtn_mean)
    abig_rtn_vol = pd.concat(cal_factor.abig_rtn_vol)
    abig_ra_corr = pd.concat(cal_factor.abig_ra_corr)

    vbig_rtn_mean.reset_index(drop=True, inplace=True)
    vbig_rtn_vol.reset_index(drop=True, inplace=True)
    vbig_rv_corr.reset_index(drop=True, inplace=True)
    abig_rtn_mean.reset_index(drop=True, inplace=True)
    abig_rtn_vol.reset_index(drop=True, inplace=True)
    abig_ra_corr.reset_index(drop=True, inplace=True)

    vbig_rtn_mean.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'vbig_rtn_mean.csv'))
    vbig_rtn_vol.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'vbig_rtn_vol.csv'))
    vbig_rv_corr.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'vbig_rv_corr.csv'))
    abig_rtn_mean.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'abig_rtn_mean.csv'))
    abig_rtn_vol.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'abig_rtn_vol.csv'))
    abig_ra_corr.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'abig_ra_corr.csv'))


if __name__ == '__main__':
    hf_big_factor('2011-01-01', '2011-03-01')

