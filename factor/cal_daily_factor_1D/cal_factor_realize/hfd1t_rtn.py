import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_daily_factor_1D.factor_test_daily1T import HFRtn
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_rtn_factor(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFRtn(
        factor_name='hf_rtn%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] == 'SA'],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    rtn_1d = pd.concat(cal_factor.rtn_1d)

    rtn_1d.reset_index(drop=True, inplace=True)

    rtn_1d.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dhf_rtn.csv'))


if __name__ == '__main__':
    hf_rtn_factor('2011-01-01', '2021-02-28')
