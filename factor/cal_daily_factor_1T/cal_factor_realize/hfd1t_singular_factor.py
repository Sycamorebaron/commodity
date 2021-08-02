import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_daily_factor_1T.factor_test_daily1T import HFSingularFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_singular_factor(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFSingularFactor(
        factor_name='hf_singular_factor_%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] == 'SA'],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()

    BV = pd.concat(cal_factor.BV).reset_index(drop=True)
    BV_sigma = pd.concat(cal_factor.BV_sigma).reset_index(drop=True)
    bollerslev_RSJ = pd.concat(cal_factor.bollerslev_RSJ).reset_index(drop=True)

    BV.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dBV.csv'))
    BV_sigma.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dBV_sigma.csv'))
    bollerslev_RSJ.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dbollerslev_RSJ.csv'))


if __name__ == '__main__':
    hf_singular_factor('2011-01-01', '2021-02-28')
