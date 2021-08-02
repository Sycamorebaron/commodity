import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_daily_factor_1T.factor_test_daily1T import HFVolPrice
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_vol_price_factor(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFVolPrice(
        factor_name='hf_vol_price_%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] == 'SA'],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()

    dvol_rtn_corr = pd.concat(cal_factor.dvol_rtn_corr).reset_index(drop=True)
    doi_rtn_corr = pd.concat(cal_factor.doi_rtn_corr).reset_index(drop=True)
    dvol_doi_corr = pd.concat(cal_factor.dvol_doi_corr).reset_index(drop=True)

    dvol_rtn_corr.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1ddvol_rtn_corr.csv'))
    doi_rtn_corr.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1ddoi_rtn_corr.csv'))
    dvol_doi_corr.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1ddvol_doi_corr.csv'))


if __name__ == '__main__':
    hf_vol_price_factor('2011-01-01', '2021-02-28')
