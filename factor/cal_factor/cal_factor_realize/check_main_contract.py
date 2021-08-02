import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_factor.factor_test import CheckMainContract
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path_5T, OUTPUT_DATA_PATH


pd.set_option('expand_frame_repr', False)

class _CheckMainContract(CheckMainContract):
    def trunc_data(self, _data):
        # 用过去一周的数据
        return CheckMainContract._trunc_data(self, _data)


def check_main_contract_cal(begin_date='2010-01-04', end_date='2021-02-28'):
    cal_factor = CheckMainContract(
        factor_name='moment',
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path_5T
    )
    cal_factor.test()

    main_contract_vol = pd.DataFrame(cal_factor.main_contract_vol)

    main_contract_vol.to_excel(os.path.join(OUTPUT_DATA_PATH, 'main_contract_vol.xlsx'))


def _check_main_contract_cal(begin_date='2010-01-04', end_date='2021-02-28'):
    cal_factor = _CheckMainContract(
        factor_name='moment',
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path_5T
    )
    cal_factor.test()

    main_contract_vol = pd.DataFrame(cal_factor.main_contract_vol)

    main_contract_vol.to_excel(os.path.join(OUTPUT_DATA_PATH, 'main_contract_vol.xlsx'))


if __name__ == '__main__':
    check_main_contract_cal(begin_date='2011-01-04')
