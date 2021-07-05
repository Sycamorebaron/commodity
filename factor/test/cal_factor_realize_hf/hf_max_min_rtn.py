import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test_hf import HFMaxMinRtn
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_leverage_effect(begin_date='2010-01-04', end_date='2021-02-28'):
    cal_factor = HFMaxMinRtn(
        factor_name='hf_rtn%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] == 'SA'],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    max_rtn = pd.concat(cal_factor.max_rtn)
    min_rtn = pd.concat(cal_factor.min_rtn)

    max_rtn.reset_index(drop=True, inplace=True)
    min_rtn.reset_index(drop=True, inplace=True)

    max_rtn.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tmax_rtn.csv'))
    min_rtn.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tmin_rtn.csv'))

if __name__ == '__main__':
    hf_leverage_effect('2011-01-01', '2021-02-28')
