import pandas as pd
import os

pd.set_option('expand_frame_repr', False)

data_path = r'D:\commodity\data\hf_comm_factor'
comm = 'FG'

data = pd.read_csv(os.path.join(data_path, '%s.csv' % comm))

factor_list = [
    'rtn', 'abig_ra_corr', 'abig_rtn_mean', 'abig_rtn_vol', 'doi_rtn_corr', 'dvol_doi_corr', 'dvol_rtn_corr',
    'd_first_com', 'd_first_com_std', 'd_oi', 'd_sec_com', 'd_sec_com_std', 'first_com_range', 'first_explained_ratio',
    'highest_rtn', 'kurt', 'lowest_rtn', 'mean', 'P0V1', 'P0V2', 'P0V3', 'P1V0', 'P2V0', 'P3V0', 'R0DV1', 'R0DV2',
    'R0DV3', 'R1DV0', 'R2DV0', 'R3DV0', 'range_pct', 'sec_com_range', 'sec_explained_ratio', 'skew', 'std',
    'vbig_rtn_mean', 'vbig_rtn_vol', 'vbig_rv_corr', 'vol_oi', 'nine', 'nine_half', 'ten', 'ten_half', 'eleven', 'one',
    'one_half', 'two'
]

data = data[['datetime'] + factor_list]
data['f_rtn'] = data['rtn'].shift(-1)

for factor in factor_list:
    print('=' * 30)
    print(factor, len(data[factor]))
    print('CORR', round(data[factor].corr(data['f_rtn']), 4))
    print('-' * 20)
    print('mean', data[factor].mean())
    print('std', data[factor].std(ddof=1))
    print('skew', data[factor].skew())
    print('kurt', data[factor].kurtosis())
    print('zero pct', round(len(data.loc[data[factor] == 0]) / len(data) * 100, 4), '%')
    print('na pct', round(len(data.loc[data[factor].isna()]) / len(data) * 100, 4), '%')
    print('-' * 20)
    print('=' * 30)




