import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_daily_factor_1D.factor_test_daily1T import HFLiquidity
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_liquidity_factor(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFLiquidity(
        factor_name='hf_liquidity_%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] == 'SA'],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()

    amihud = pd.concat(cal_factor.amihud).reset_index(drop=True)
    roll_spread = pd.concat(cal_factor.roll_spread).reset_index(drop=True)
    LOT = pd.concat(cal_factor.LOT).reset_index(drop=True)
    pastor_gamma = pd.concat(cal_factor.pastor_gamma).reset_index(drop=True)


    amihud.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1damihud.csv'))
    roll_spread.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1droll_spread.csv'))
    LOT.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dLOT.csv'))
    pastor_gamma.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dpastor_gamma.csv'))


if __name__ == '__main__':
    hf_liquidity_factor('2011-01-01', '2021-02-28')
