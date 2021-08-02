import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_factor.factor_test import BigFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH


pd.set_option('expand_frame_repr', False)


class _BigFactor(BigFactor):
    def trunc_data(self, _data):
        return BigFactor._trunc_data(self, _data)


def big_factor_cal(begin_date='2010-01-04', end_date='2021-02-28'):
    cal_factor = BigFactor(
        factor_name='moment',
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()

    l_vbig_rtn_mean = pd.DataFrame(cal_factor.vbig_rtn_mean)
    l_vbig_rtn_vol = pd.DataFrame(cal_factor.vbig_rtn_vol)
    l_vbig_rv_corr = pd.DataFrame(cal_factor.vbig_rv_corr)

    l_abig_rtn_mean = pd.DataFrame(cal_factor.abig_rtn_mean)
    l_abig_rtn_vol = pd.DataFrame(cal_factor.abig_rtn_vol)
    l_abig_ra_corr = pd.DataFrame(cal_factor.abig_ra_corr)

    l_vbig_rtn_mean.to_excel(os.path.join(OUTPUT_DATA_PATH, 'vbig_rtn_mean.xlsx'))
    l_vbig_rtn_vol.to_excel(os.path.join(OUTPUT_DATA_PATH, 'vbig_rtn_vol.xlsx'))
    l_vbig_rv_corr.to_excel(os.path.join(OUTPUT_DATA_PATH, 'vbig_rv_corr.xlsx'))

    l_abig_rtn_mean.to_excel(os.path.join(OUTPUT_DATA_PATH, 'abig_rtn_mean.xlsx'))
    l_abig_rtn_vol.to_excel(os.path.join(OUTPUT_DATA_PATH, 'abig_rtn_vol.xlsx'))
    l_abig_ra_corr.to_excel(os.path.join(OUTPUT_DATA_PATH, 'abig_ra_corr.xlsx'))


def _big_factor_cal(begin_date='2010-01-04', end_date='2021-02-28'):
    cal_factor = _BigFactor(
        factor_name='moment',
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()

    l_vbig_rtn_mean = pd.DataFrame(cal_factor.vbig_rtn_mean)
    l_vbig_rtn_vol = pd.DataFrame(cal_factor.vbig_rtn_vol)
    l_vbig_rv_corr = pd.DataFrame(cal_factor.vbig_rv_corr)

    l_abig_rtn_mean = pd.DataFrame(cal_factor.abig_rtn_mean)
    l_abig_rtn_vol = pd.DataFrame(cal_factor.abig_rtn_vol)
    l_abig_ra_corr = pd.DataFrame(cal_factor.abig_ra_corr)

    l_vbig_rtn_mean.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_vbig_rtn_mean.xlsx'))
    l_vbig_rtn_vol.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_vbig_rtn_vol.xlsx'))
    l_vbig_rv_corr.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_vbig_rv_corr.xlsx'))

    l_abig_rtn_mean.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_abig_rtn_mean.xlsx'))
    l_abig_rtn_vol.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_abig_rtn_vol.xlsx'))
    l_abig_ra_corr.to_excel(os.path.join(OUTPUT_DATA_PATH, '5D_abig_ra_corr.xlsx'))


if __name__ == '__main__':

    big_factor_cal()
