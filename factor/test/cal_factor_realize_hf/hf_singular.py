import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test_hf import HFSingularFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_singular(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFSingularFactor(
        factor_name='hf_rtn%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    BV = pd.concat(cal_factor.BV)
    BV_sigma = pd.concat(cal_factor.BV_sigma)
    bollerslev_RSJ = pd.concat(cal_factor.bollerslev_RSJ)

    BV.reset_index(drop=True, inplace=True)
    BV_sigma.reset_index(drop=True, inplace=True)
    bollerslev_RSJ.reset_index(drop=True, inplace=True)

    BV.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'BV.csv'))
    BV_sigma.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'BV_sigma.csv'))
    bollerslev_RSJ.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'bollerslev_RSJ.csv'))


if __name__ == '__main__':
    hf_singular('2011-01-01', '2011-03-01')

