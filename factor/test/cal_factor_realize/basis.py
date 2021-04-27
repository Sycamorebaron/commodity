import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test import BasisFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path_5T, OUTPUT_DATA_PATH


pd.set_option('expand_frame_repr', False)

class _BasisFactor(BasisFactor):
    def trunc_data(self, _data):
        return BasisFactor._trunc_data(self, _data)


def basis_cal(begin_date='2010-01-04', end_date='2021-02-28'):
    cal_factor = BasisFactor(
        factor_name='moment',
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path_5T
    )
    cal_factor.test()

    l_main_sec_basis = pd.DataFrame(cal_factor.main_sec_basis)
    l_open_basis = pd.DataFrame(cal_factor.open_basis)
    l_close_basis = pd.DataFrame(cal_factor.close_basis)
    l_main_sec_basis_rv = pd.DataFrame(cal_factor.main_sec_basis_rv)
    l_mean_basis = pd.DataFrame(cal_factor.mean_basis)

    l_main_sec_basis.to_excel(os.path.join(OUTPUT_DATA_PATH, 'main_sec_basis.xlsx'))
    l_open_basis.to_excel(os.path.join(OUTPUT_DATA_PATH, 'open_basis.xlsx'))
    l_close_basis.to_excel(os.path.join(OUTPUT_DATA_PATH, 'close_basis.xlsx'))
    l_main_sec_basis_rv.to_excel(os.path.join(OUTPUT_DATA_PATH, 'main_sec_basis_rv.xlsx'))
    l_mean_basis.to_excel(os.path.join(OUTPUT_DATA_PATH, 'mean_basis.xlsx'))


def _basis_cal(begin_date='2010-01-04', end_date='2021-02-28'):
    cal_factor = _BasisFactor(
        factor_name='moment',
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path_5T
    )
    cal_factor.test()

    l_main_sec_basis = pd.DataFrame(cal_factor.main_sec_basis)
    l_main_sec_basis_rv = pd.DataFrame(cal_factor.main_sec_basis_rv)
    l_mean_basis = pd.DataFrame(cal_factor.mean_basis)

    l_main_sec_basis.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_main_sec_basis.xlsx'))
    l_main_sec_basis_rv.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_main_sec_basis_rv.xlsx'))
    l_mean_basis.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_mean_basis.xlsx'))



if __name__ == '__main__':
    _basis_cal(begin_date='2013-02-04')