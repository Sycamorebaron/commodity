import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test import PCAFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path_5T, OUTPUT_DATA_PATH


pd.set_option('expand_frame_repr', False)


def pca_factor_cal():
    cal_factor = PCAFactor(
        factor_name='moment',
        begin_date='2010-01-04',
        end_date='2021-02-28',
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path_5T
    )
    cal_factor.test()

    l_d_first_com = pd.DataFrame(cal_factor.d_first_com)
    l_d_sec_com = pd.DataFrame(cal_factor.d_sec_com)
    l_first_com_range = pd.DataFrame(cal_factor.first_com_range)
    l_sec_com_range = pd.DataFrame(cal_factor.sec_com_range)
    l_d_first_com_std = pd.DataFrame(cal_factor.d_first_com_std)
    l_d_sec_com_std = pd.DataFrame(cal_factor.d_sec_com_std)
    l_first_explained_ratio = pd.DataFrame(cal_factor.first_explained_ratio)
    l_sec_explained_ratio = pd.DataFrame(cal_factor.sec_explained_ratio)

    l_d_first_com.to_excel(os.path.join(OUTPUT_DATA_PATH, 'd_first_com.xlsx'))
    l_d_sec_com.to_excel(os.path.join(OUTPUT_DATA_PATH, 'd_sec_com.xlsx'))
    l_first_com_range.to_excel(os.path.join(OUTPUT_DATA_PATH, 'first_com_range.xlsx'))
    l_sec_com_range.to_excel(os.path.join(OUTPUT_DATA_PATH, 'sec_com_range.xlsx'))
    l_d_first_com_std.to_excel(os.path.join(OUTPUT_DATA_PATH, 'd_first_com_std.xlsx'))
    l_d_sec_com_std.to_excel(os.path.join(OUTPUT_DATA_PATH, 'd_sec_com_std.xlsx'))
    l_first_explained_ratio.to_excel(os.path.join(OUTPUT_DATA_PATH, 'first_explained_ratio.xlsx'))
    l_sec_explained_ratio.to_excel(os.path.join(OUTPUT_DATA_PATH, 'sec_explained_ratio.xlsx'))


if __name__ == '__main__':

    pca_factor_cal()
