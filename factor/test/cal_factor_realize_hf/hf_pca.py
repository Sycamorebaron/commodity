import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test_hf import HFPCAFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_pca_price(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFPCAFactor(
        factor_name='hf_rtn%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] == 'L'],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    d_first_com = pd.concat(cal_factor.d_first_com)
    d_sec_com = pd.concat(cal_factor.d_sec_com)
    first_com_range = pd.concat(cal_factor.first_com_range)
    sec_com_range = pd.concat(cal_factor.sec_com_range)
    d_first_com_std = pd.concat(cal_factor.d_first_com_std)
    d_sec_com_std = pd.concat(cal_factor.d_sec_com_std)
    first_explained_ratio = pd.concat(cal_factor.first_explained_ratio)
    sec_explained_ratio = pd.concat(cal_factor.sec_explained_ratio)

    d_first_com.reset_index(drop=True, inplace=True)
    d_sec_com.reset_index(drop=True, inplace=True)
    first_com_range.reset_index(drop=True, inplace=True)
    sec_com_range.reset_index(drop=True, inplace=True)
    d_first_com_std.reset_index(drop=True, inplace=True)
    d_sec_com_std.reset_index(drop=True, inplace=True)
    first_explained_ratio.reset_index(drop=True, inplace=True)
    sec_explained_ratio.reset_index(drop=True, inplace=True)

    d_first_com.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'd_first_com.csv'))
    d_sec_com.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'd_sec_com.csv'))
    first_com_range.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'first_com_range.csv'))
    sec_com_range.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'sec_com_range.csv'))
    d_first_com_std.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'd_first_com_std.csv'))
    d_sec_com_std.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'd_sec_com_std.csv'))
    first_explained_ratio.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'first_explained_ratio.csv'))
    sec_explained_ratio.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'sec_explained_ratio.csv'))


if __name__ == '__main__':
    hf_pca_price('2011-01-01', '2021-02-28')

