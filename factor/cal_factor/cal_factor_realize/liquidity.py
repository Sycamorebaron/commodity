import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_factor.factor_test import Liquidity
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH


pd.set_option('expand_frame_repr', False)


class _Liquidity(Liquidity):
    def trunc_data(self, _data):
        return Liquidity._trunc_data(self, _data)


def liquidity_cal(begin_date='2010-01-04', end_date='2021-02-28'):
    cal_factor = Liquidity(
        factor_name='moment',
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()

    l_amihud = pd.DataFrame(cal_factor.amihud)
    l_roll_spread = pd.DataFrame(cal_factor.roll_spread)
    l_LOT = pd.DataFrame(cal_factor.LOT)
    l_pastor_gamma = pd.DataFrame(cal_factor.pastor_gamma)


    l_amihud.to_excel(os.path.join(OUTPUT_DATA_PATH, 'amihud.xlsx'))
    l_roll_spread.to_excel(os.path.join(OUTPUT_DATA_PATH, 'roll_spread.xlsx'))
    l_LOT.to_excel(os.path.join(OUTPUT_DATA_PATH, 'LOT.xlsx'))
    l_pastor_gamma.to_excel(os.path.join(OUTPUT_DATA_PATH, 'pastor_gamma.xlsx'))


def _liquidity_cal(begin_date='2010-01-04', end_date='2021-02-28'):
    cal_factor = _Liquidity(
        factor_name='moment',
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()

    l_amihud = pd.DataFrame(cal_factor.amihud)
    l_roll_spread = pd.DataFrame(cal_factor.roll_spread)
    l_LOT = pd.DataFrame(cal_factor.LOT)
    l_pastor_gamma = pd.DataFrame(cal_factor.pastor_gamma)


    l_amihud.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_amihud.xlsx'))
    l_roll_spread.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_roll_spread.xlsx'))
    l_LOT.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_LOT.xlsx'))
    l_pastor_gamma.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_pastor_gamma.xlsx'))


if __name__ == '__main__':

    liquidity_cal()
