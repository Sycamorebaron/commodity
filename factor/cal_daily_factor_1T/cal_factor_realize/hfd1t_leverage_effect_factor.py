import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_daily_factor_1T.factor_test_daily1T import HFLeverageEffect
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_leverage_effect_factor(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFLeverageEffect(
        factor_name='hf_leverage_effect_factor_%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] == 'SA'],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()

    BV_rtn = pd.concat(cal_factor.BV_rtn).reset_index(drop=True)
    std_rtn = pd.concat(cal_factor.std_rtn).reset_index(drop=True)

    BV_rtn.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dBV_rtn.csv'))
    std_rtn.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dstd_rtn.csv'))


if __name__ == '__main__':
    hf_leverage_effect_factor('2011-01-01', '2021-02-28')