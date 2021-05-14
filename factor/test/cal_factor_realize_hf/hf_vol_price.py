import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test_hf import HFVolPrice
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_vol_pirce(begin_date='2011-01-01', end_date='2021-02-28'):

    cal_factor = HFVolPrice(
        factor_name='hf_rtn%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        # contract_list=[x for x in NORMAL_CONTRACT_INFO if x['id'] == 'SA'],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    dvol_rtn_corr = pd.concat(cal_factor.dvol_rtn_corr)
    doi_rtn_corr = pd.concat(cal_factor.doi_rtn_corr)
    dvol_doi_corr = pd.concat(cal_factor.dvol_doi_corr)

    dvol_rtn_corr.reset_index(drop=True, inplace=True)
    doi_rtn_corr.reset_index(drop=True, inplace=True)
    dvol_doi_corr.reset_index(drop=True, inplace=True)

    dvol_rtn_corr.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'dvol_rtn_corr.csv'))
    doi_rtn_corr.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'doi_rtn_corr.csv'))
    dvol_doi_corr.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'dvol_doi_corr.csv'))

if __name__ == '__main__':
    hf_vol_pirce()

