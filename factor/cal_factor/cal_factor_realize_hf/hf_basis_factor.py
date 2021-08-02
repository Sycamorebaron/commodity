import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_factor.factor_test_hf import HFBasisFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_basis_factor(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFBasisFactor(
        factor_name='hf_rtn%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] == 'SA'],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    main_sec_basis = pd.concat(cal_factor.main_sec_basis)
    d_main_sec_basis = pd.concat(cal_factor.d_main_sec_basis)
    dbdv = pd.concat(cal_factor.dbdv)
    dbdoi = pd.concat(cal_factor.dbdoi)


    main_sec_basis.reset_index(drop=True, inplace=True)
    d_main_sec_basis.reset_index(drop=True, inplace=True)
    dbdv.reset_index(drop=True, inplace=True)
    dbdoi.reset_index(drop=True, inplace=True)


    main_sec_basis.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tmain_sec_basis.csv'))
    d_main_sec_basis.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Td_main_sec_basis.csv'))
    dbdv.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tdbdv.csv'))
    dbdoi.to_csv(os.path.join(OUTPUT_DATA_PATH, '15THFfactor', '15Tdbdoi.csv'))


if __name__ == '__main__':
    hf_basis_factor('2011-01-01', '2021-02-28')
