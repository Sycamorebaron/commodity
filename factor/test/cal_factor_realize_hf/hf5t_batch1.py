import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test_5T import HF5TBatch1
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_5t_bacth1(begin_date='2011-01-01', end_date='2021-02-28'):
    cal_factor = HF5TBatch1(
        factor_name='moment',
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] in ['L', 'M', 'C']],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    mean_5t = pd.concat(cal_factor.mean_5t)
    lowest_rtn_5t = pd.concat(cal_factor.lowest_rtn_5t)
    highest_rtn_5t = pd.concat(cal_factor.highest_rtn_5t)
    amihud = pd.concat(cal_factor.amihud)
    doi_pct = pd.concat(cal_factor.doi_pct)

    mean_5t.reset_index(drop=True, inplace=True)
    lowest_rtn_5t.reset_index(drop=True, inplace=True)
    highest_rtn_5t.reset_index(drop=True, inplace=True)
    amihud.reset_index(drop=True, inplace=True)
    doi_pct.reset_index(drop=True, inplace=True)

    mean_5t.to_csv(os.path.join(OUTPUT_DATA_PATH, '5THFfactor', '5Tmean.csv'))
    lowest_rtn_5t.to_csv(os.path.join(OUTPUT_DATA_PATH, '5THFfactor', '5Tlowest_rtn.csv'))
    highest_rtn_5t.to_csv(os.path.join(OUTPUT_DATA_PATH, '5THFfactor', '5Thighest_rtn.csv'))
    amihud.to_csv(os.path.join(OUTPUT_DATA_PATH, '5THFfactor', '5Tamihud.csv'))
    doi_pct.to_csv(os.path.join(OUTPUT_DATA_PATH, '5THFfactor', '5Tdoi_pct.csv'))


if __name__ == '__main__':
    hf_5t_bacth1()
