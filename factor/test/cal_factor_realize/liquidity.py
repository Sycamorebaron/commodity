import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test import Liquidity
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH


pd.set_option('expand_frame_repr', False)


def liquidity_cal():
    cal_factor = Liquidity(
        factor_name='moment',
        begin_date='2010-01-01',
        end_date='2021-02-28',
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


if __name__ == '__main__':

    liquidity_cal()