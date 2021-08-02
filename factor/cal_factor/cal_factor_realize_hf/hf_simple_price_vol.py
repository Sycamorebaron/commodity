import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_factor.factor_test_hf import HFSimplePriceVolumeFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_simple_price_vol(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFSimplePriceVolumeFactor(
        factor_name='hf_rtn%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] == 'L'],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    highest_rtn = pd.concat(cal_factor.highest_rtn)
    lowest_rtn = pd.concat(cal_factor.lowest_rtn)
    range_pct = pd.concat(cal_factor.range_pct)
    vol_oi = pd.concat(cal_factor.vol_oi)
    d_oi = pd.concat(cal_factor.d_oi)


    highest_rtn.reset_index(drop=True, inplace=True)
    lowest_rtn.reset_index(drop=True, inplace=True)
    range_pct.reset_index(drop=True, inplace=True)
    vol_oi.reset_index(drop=True, inplace=True)
    d_oi.reset_index(drop=True, inplace=True)


    highest_rtn.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Thighest_rtn.csv'))
    lowest_rtn.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tlowest_rtn.csv'))
    range_pct.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Trange_pct.csv'))
    vol_oi.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tvol_oi.csv'))
    d_oi.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Td_oi.csv'))


if __name__ == '__main__':
    hf_simple_price_vol('2011-01-01', '2021-02-28')

