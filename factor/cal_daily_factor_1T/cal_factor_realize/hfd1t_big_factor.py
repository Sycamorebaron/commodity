import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_daily_factor_1T.factor_test_daily1T import HFBigFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_big_factor(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFBigFactor(
        factor_name='hf_big_factor_%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] == 'SA'],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()

    vbig_rtn_mean = pd.concat(cal_factor.vbig_rtn_mean).reset_index(drop=True)
    vbig_rtn_vol = pd.concat(cal_factor.vbig_rtn_vol).reset_index(drop=True)
    vbig_rv_corr = pd.concat(cal_factor.vbig_rv_corr).reset_index(drop=True)
    abig_rtn_mean = pd.concat(cal_factor.abig_rtn_mean).reset_index(drop=True)
    abig_rtn_vol = pd.concat(cal_factor.abig_rtn_vol).reset_index(drop=True)
    abig_ra_corr = pd.concat(cal_factor.abig_ra_corr).reset_index(drop=True)

    vbig_rtn_mean.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dvbig_rtn_mean.csv'))
    vbig_rtn_vol.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dvbig_rtn_vol.csv'))
    vbig_rv_corr.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dvbig_rv_corr.csv'))
    abig_rtn_mean.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dabig_rtn_mean.csv'))
    abig_rtn_vol.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dabig_rtn_vol.csv'))
    abig_ra_corr.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dabig_ra_corr.csv'))


if __name__ == '__main__':
    hf_pca_factor('2011-01-01', '2021-02-28')