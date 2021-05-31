import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test_hf import HFRtnMoment
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_rtn_moment(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFRtnMoment(
        factor_name='hf_rtn%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    mean = pd.concat(cal_factor.mean)
    std = pd.concat(cal_factor.std)
    skew = pd.concat(cal_factor.skew)
    kurt = pd.concat(cal_factor.kurt)

    mean.reset_index(drop=True, inplace=True)
    std.reset_index(drop=True, inplace=True)
    skew.reset_index(drop=True, inplace=True)
    kurt.reset_index(drop=True, inplace=True)

    mean.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tmean.csv'))
    std.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tstd.csv'))
    skew.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tskew.csv'))
    kurt.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tkurt.csv'))

if __name__ == '__main__':
    hf_rtn_moment('2011-01-01', '2011-03-01')

