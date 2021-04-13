import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.test.factor_test import MoneyFlow
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path_5T, OUTPUT_DATA_PATH


pd.set_option('expand_frame_repr', False)


def money_flow_cal():
    cal_factor = MoneyFlow(
        factor_name='moment',
        begin_date='2010-01-04',
        end_date='2021-02-28',
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path_5T
    )
    cal_factor.test()

    l_money_flow = pd.DataFrame(cal_factor.money_flow)

    l_money_flow.to_excel(os.path.join(OUTPUT_DATA_PATH, 'money_flow.xlsx'))


if __name__ == '__main__':

    money_flow_cal()
