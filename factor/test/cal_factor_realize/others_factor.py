import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test import Others
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)


def others_factor_cal():

    cal_factor = Others(
        factor_name='moment',
        begin_date='2010-01-01',
        end_date='2021-02-28',
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )

    cal_factor.test()
    l_smart_money_vol_pct = pd.DataFrame(cal_factor.smart_money_vol_pct)
    l_CVaR = pd.DataFrame(cal_factor.CVaR)
    l_VCVaR = pd.DataFrame(cal_factor.VCVaR)
    l_vwap_move_pct = pd.DataFrame(cal_factor.vwap_move_pct)

    l_smart_money_vol_pct.to_excel(os.path.join(OUTPUT_DATA_PATH, 'smart_money_vol_pct.xlsx'))
    l_CVaR.to_excel(os.path.join(OUTPUT_DATA_PATH, 'CVaR.xlsx'))
    l_VCVaR.to_excel(os.path.join(OUTPUT_DATA_PATH, 'VCVaR.xlsx'))
    l_vwap_move_pct.to_excel(os.path.join(OUTPUT_DATA_PATH, 'vwap_move_pct.xlsx'))


if __name__ == '__main__':
    others_factor_cal()
