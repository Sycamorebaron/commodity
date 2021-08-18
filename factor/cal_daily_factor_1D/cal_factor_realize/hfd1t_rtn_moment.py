import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_daily_factor_1D.factor_test_daily1T import HFRtnMoment
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_rtn_moment_factor(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFRtnMoment(
        factor_name='hf_rtn_moment%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] == 'SA'],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    mean = pd.concat(cal_factor.mean)
    std = pd.concat(cal_factor.std)
    skew = pd.concat(cal_factor.skew)
    kurt = pd.concat(cal_factor.kurt)

    mean.reset_index(drop=True, inplace=True)
    std.reset_index(drop=True, inplace=True)
    skew.reset_index(drop=True, inplace=True)
    kurt.reset_index(drop=True, inplace=True)

    mean.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dmean.csv'))
    std.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dstd.csv'))
    skew.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dskew.csv'))
    kurt.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dkurt.csv'))


if __name__ == '__main__':
    hf_rtn_moment_factor('2011-01-01', '2021-02-28')
