import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test import RtnMoment
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH


pd.set_option('expand_frame_repr', False)


if __name__ == '__main__':
    if __name__ == '__main__':
        cal_factor = RtnMoment(
            factor_name='moment',
            begin_date='2010-01-04',
            end_date='2021-02-28',
            init_cash=1000000,
            contract_list=NORMAL_CONTRACT_INFO,
            local_data_path=local_data_path
        )
        cal_factor.test()

        l_rtn_mean = pd.DataFrame(cal_factor.mean)
        l_rtn_std = pd.DataFrame(cal_factor.std)
        l_rtn_skew = pd.DataFrame(cal_factor.skew)
        l_rtn_kurt = pd.DataFrame(cal_factor.kurt)

        l_rtn_mean.to_excel(os.path.join(OUTPUT_DATA_PATH, 'rtn_mean.xlsx'))
        l_rtn_std.to_excel(os.path.join(OUTPUT_DATA_PATH, 'rtn_std.xlsx'))
        l_rtn_skew.to_excel(os.path.join(OUTPUT_DATA_PATH, 'rtn_skew.xlsx'))
        l_rtn_kurt.to_excel(os.path.join(OUTPUT_DATA_PATH, 'rtn_kurt.xlsx'))
