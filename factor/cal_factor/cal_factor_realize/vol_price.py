import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_factor.factor_test import VolPrice
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path_5T, OUTPUT_DATA_PATH


pd.set_option('expand_frame_repr', False)


class _VolPrice(VolPrice):
    def trunc_data(self, _data):
        return VolPrice._trunc_data(self, _data)


def vol_price_cal(begin_date='2010-01-04', end_date='2021-02-28'):
    cal_factor = VolPrice(
        factor_name='moment',
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path_5T
    )
    cal_factor.test()

    l_dvol_rtn_corr = pd.DataFrame(cal_factor.dvol_rtn_corr)
    l_doi_rtn_corr = pd.DataFrame(cal_factor.doi_rtn_corr)
    l_dvol_doi_corr = pd.DataFrame(cal_factor.dvol_doi_corr)

    l_dvol_rtn_corr.to_excel(os.path.join(OUTPUT_DATA_PATH, 'dvol_rtn_corr.xlsx'))
    l_doi_rtn_corr.to_excel(os.path.join(OUTPUT_DATA_PATH, 'doi_rtn_corr.xlsx'))
    l_dvol_doi_corr.to_excel(os.path.join(OUTPUT_DATA_PATH, 'dvol_doi_corr.xlsx'))


def _vol_price_cal(begin_date='2010-01-04', end_date='2021-02-28'):
    cal_factor = _VolPrice(
        factor_name='moment',
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path_5T
    )
    cal_factor.test()

    l_dvol_rtn_corr = pd.DataFrame(cal_factor.dvol_rtn_corr)
    l_doi_rtn_corr = pd.DataFrame(cal_factor.doi_rtn_corr)
    l_dvol_doi_corr = pd.DataFrame(cal_factor.dvol_doi_corr)

    l_dvol_rtn_corr.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_dvol_rtn_corr.xlsx'))
    l_doi_rtn_corr.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_doi_rtn_corr.xlsx'))
    l_dvol_doi_corr.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_dvol_doi_corr.xlsx'))


if __name__ == '__main__':
    vol_price_cal()