import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_daily_factor_1D.factor_test_daily1T import HFContinuousContract
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_continuous_contract_factor(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFContinuousContract(
        factor_name='hf_pv_corr_factor_%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] == 'SA'],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()

    close_open = pd.concat(cal_factor.close_open).reset_index(drop=True)
    close_high = pd.concat(cal_factor.close_high).reset_index(drop=True)
    close_low = pd.concat(cal_factor.close_low).reset_index(drop=True)
    close_close = pd.concat(cal_factor.close_close).reset_index(drop=True)
    oi_oi = pd.concat(cal_factor.oi_oi).reset_index(drop=True)
    vol_vol = pd.concat(cal_factor.vol_vol).reset_index(drop=True)

    close_open.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dclose_open.csv'))
    close_high.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dclose_high.csv'))
    close_low.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dclose_low.csv'))
    close_close.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dclose_close.csv'))
    oi_oi.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1doi_oi.csv'))
    vol_vol.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dvol_vol.csv'))


if __name__ == '__main__':
    hf_continuous_contract_factor('2011-01-01', '2021-02-28')
