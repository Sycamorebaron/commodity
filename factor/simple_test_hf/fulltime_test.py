import pandas as pd
import os

pd.set_option('expand_frame_repr', False)

data_path = r'D:\commodity\data\hf_comm_factor'
comm = 'FG'

data = pd.read_csv(os.path.join(data_path, '%s.csv' % comm))
factor_list = [
    'rtn', 'abig_ra_corr', 'abig_rtn_mean', 'abig_rtn_vol', 'doi_rtn_corr', 'dvol_doi_corr', 'dvol_rtn_corr',
    'd_first_com', 'd_first_com_std', 'd_sec_com', 'd_sec_com_std', 'first_com_range',  'first_explained_ratio', 'kurt',
    'mean', 'sec_com_range', 'sec_explained_ratio', 'skew', 'std', 'vbig_rtn_mean', 'vbig_rtn_vol', 'vbig_rv_corr',
    'nine', 'nine_half', 'ten', 'ten_half', 'eleven', 'one', 'one_half', 'two',
]

data = data[['datetime'] + factor_list]

for factor in factor_list:
    print('=' * 30)
    print(factor, len(data[factor]))
    print('mean', data[factor].mean())
    print('std', data[factor].std(ddof=1))
    print('skew', data[factor].skew())
    print('kurt', data[factor].kurtosis())
    print('zero pct', len(data.loc[data[factor] == 0]) / len(data) * 100)
    print('na pct', len(data.loc[data[factor].isna()]) / len(data) * 100)
    print('=' * 30)


