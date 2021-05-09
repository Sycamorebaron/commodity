import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test_hf import HFLiquidity
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_liquidity_pirce(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFLiquidity(
        factor_name='hf_rtn%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    amihud = pd.concat(cal_factor.amihud)
    roll_spread = pd.concat(cal_factor.roll_spread)
    LOT = pd.concat(cal_factor.LOT)
    pastor_gamma = pd.concat(cal_factor.pastor_gamma)

    amihud.reset_index(drop=True, inplace=True)
    roll_spread.reset_index(drop=True, inplace=True)
    LOT.reset_index(drop=True, inplace=True)
    pastor_gamma.reset_index(drop=True, inplace=True)

    amihud.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'amihud.csv'))
    roll_spread.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'roll_spread.csv'))
    LOT.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'LOT.csv'))
    pastor_gamma.to_csv(os.path.join(OUTPUT_DATA_PATH, 'HFfactor', 'pastor_gamma.csv'))


if __name__ == '__main__':
    hf_liquidity_pirce('2011-01-01', '2011-03-01')

