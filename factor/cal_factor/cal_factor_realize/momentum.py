import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_factor.factor_test import MomentumFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path_5T, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)


class _MomentumFactor(MomentumFactor):
    def trunc_data(self, _data):
        return MomentumFactor._trunc_data(self, _data)


def momentum_cal(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = MomentumFactor(
        factor_name='moment',
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path_5T
    )

    cal_factor.test()
    l_up_move_pct = pd.DataFrame(cal_factor.up_move_pct)
    l_except_last_30t = pd.DataFrame(cal_factor.except_last_30t)

    l_up_move_pct.to_excel(os.path.join(OUTPUT_DATA_PATH, 'up_move.xlsx'))
    l_except_last_30t.to_excel(os.path.join(OUTPUT_DATA_PATH, 'except_last_30t.xlsx'))


def _momentum_cal(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = _MomentumFactor(
        factor_name='moment',
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path_5T
    )

    cal_factor.test()
    l_up_move_pct = pd.DataFrame(cal_factor.up_move_pct)

    l_up_move_pct.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_up_move.xlsx'))


if __name__ == '__main__':
    momentum_cal()