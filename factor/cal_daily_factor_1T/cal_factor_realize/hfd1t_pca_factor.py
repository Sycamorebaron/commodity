import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_daily_factor_1T.factor_test_daily1T import HFPCAFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_pca_factor(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFPCAFactor(
        factor_name='hf_pca_%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] == 'SA'],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()

    d_first_com = pd.concat(cal_factor.d_first_com).reset_index(drop=True)
    d_sec_com = pd.concat(cal_factor.d_sec_com).reset_index(drop=True)
    first_com_range = pd.concat(cal_factor.first_com_range).reset_index(drop=True)
    sec_com_range = pd.concat(cal_factor.sec_com_range).reset_index(drop=True)
    d_first_com_std = pd.concat(cal_factor.d_first_com_std).reset_index(drop=True)
    d_sec_com_std = pd.concat(cal_factor.d_sec_com_std).reset_index(drop=True)
    first_explained_ratio = pd.concat(cal_factor.first_explained_ratio).reset_index(drop=True)
    sec_explained_ratio = pd.concat(cal_factor.sec_explained_ratio).reset_index(drop=True)

    d_first_com.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dd_first_com.csv'))
    d_sec_com.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dd_sec_com.csv'))
    first_com_range.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dfirst_com_range.csv'))
    sec_com_range.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dsec_com_range.csv'))
    d_first_com_std.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dd_first_com_std.csv'))
    d_sec_com_std.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dd_sec_com_std.csv'))
    first_explained_ratio.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dfirst_explained_ratio.csv'))
    sec_explained_ratio.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dsec_explained_ratio.csv'))


if __name__ == '__main__':
    hf_pca_factor('2011-01-01', '2021-02-28')
