import sys
import os
import pandas as pd
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(BASE_DIR)

from factor.cal_daily_factor_1T.factor_test_daily1T import HFPVCorrFactor
from utils.base_para import NORMAL_CONTRACT_INFO, local_data_path, OUTPUT_DATA_PATH

pd.set_option('expand_frame_repr', False)

def hf_PVCorr_factor(begin_date='2010-01-04', end_date='2021-02-28'):

    cal_factor = HFPVCorrFactor(
        factor_name='hf_pv_corr_factor_%s_%s' % (begin_date, end_date),
        begin_date=begin_date,
        end_date=end_date,
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] == 'SA'],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()

    P1V0 = pd.concat(cal_factor.P1V0).reset_index(drop=True)
    P2V0 = pd.concat(cal_factor.P2V0).reset_index(drop=True)
    P3V0 = pd.concat(cal_factor.P3V0).reset_index(drop=True)
    P0V1 = pd.concat(cal_factor.P0V1).reset_index(drop=True)
    P0V2 = pd.concat(cal_factor.P0V2).reset_index(drop=True)
    P0V3 = pd.concat(cal_factor.P0V3).reset_index(drop=True)

    R1DV0 = pd.concat(cal_factor.R1DV0).reset_index(drop=True)
    R2DV0 = pd.concat(cal_factor.R2DV0).reset_index(drop=True)
    R3DV0 = pd.concat(cal_factor.R3DV0).reset_index(drop=True)
    R0DV1 = pd.concat(cal_factor.R0DV1).reset_index(drop=True)
    R0DV2 = pd.concat(cal_factor.R0DV2).reset_index(drop=True)
    R0DV3 = pd.concat(cal_factor.R0DV3).reset_index(drop=True)

    P1V0.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dP1V0.csv'))
    P2V0.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dP2V0.csv'))
    P3V0.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dP3V0.csv'))
    P0V1.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dP0V1.csv'))
    P0V2.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dP0V2.csv'))
    P0V3.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dP0V3.csv'))

    R1DV0.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dR1DV0.csv'))
    R2DV0.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dR2DV0.csv'))
    R3DV0.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dR3DV0.csv'))
    R0DV1.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dR0DV1.csv'))
    R0DV2.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dR0DV2.csv'))
    R0DV3.to_csv(os.path.join(OUTPUT_DATA_PATH, '1DHFfactor', '1dR0DV3.csv'))


if __name__ == '__main__':
    hf_PVCorr_factor('2011-01-01', '2021-02-28')
