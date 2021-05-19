import pandas as pd
import os

pd.set_option('expand_frame_repr', False)

data_path = r'D:\commodity\data\hf_comm_factor'

factor_list = [
    'abig_ra_corr', 'abig_rtn_mean', 'abig_rtn_vol', 'doi_rtn_corr', 'dvol_doi_corr', 'dvol_rtn_corr',
    'd_first_com', 'd_first_com_std', 'd_oi', 'd_sec_com', 'd_sec_com_std', 'first_com_range', 'first_explained_ratio',
    'highest_rtn', 'kurt', 'lowest_rtn', 'mean', 'P0V1', 'P0V2', 'P0V3', 'P1V0', 'P2V0', 'P3V0', 'R0DV1', 'R0DV2',
    'R0DV3', 'R1DV0', 'R2DV0', 'R3DV0', 'range_pct', 'sec_com_range', 'sec_explained_ratio', 'skew', 'std',
    'vbig_rtn_mean', 'vbig_rtn_vol', 'vbig_rv_corr', 'vol_oi', 'nine', 'nine_half', 'ten', 'ten_half', 'eleven', 'one',
    'one_half', 'two'
]

local_files = []
for roots, dirs, files in os.walk(data_path):
    if files:
        local_files = files

for factor in factor_list:
    print('TEST', factor)
    factor_ic = []
    factor_sum_data = pd.DataFrame()
    for comm in local_files:
        data = pd.read_csv(os.path.join(data_path, comm))
        data['%s_f_rtn' % comm] = data['rtn'].shift(-1)
        data = data[['datetime', factor, '%s_f_rtn' % comm]].copy()
        data.columns = ['datetime', comm.split('.')[0], '%s_f_rtn' % comm.split('.')[0]]
        if len(factor_sum_data):
            factor_sum_data = factor_sum_data.merge(data, on='datetime', how='outer')
        else:
            factor_sum_data = data
    for i in range(len(factor_sum_data)):
        dt = factor_sum_data['datetime'].iloc[i]
        print(dt)
        t_data = pd.DataFrame(factor_sum_data.iloc[i]).reset_index()
        t_data = t_data.dropna(subset=[i])[1:].reset_index(drop=True)
        factor_df = t_data.loc[t_data['index'].apply(lambda x: not x.endswith('f_rtn'))].copy()
        f_rtn_df = t_data.loc[t_data['index'].apply(lambda x: x.endswith('f_rtn'))].copy()
        f_rtn_df['index'] = f_rtn_df['index'].apply(lambda x: x.split('_')[0])
        f_rtn_df.columns = ['comm', 'f_rtn']
        factor_df.columns = ['comm', 'factor']
        t_factor_df = f_rtn_df.merge(factor_df, on='comm', how='inner')
        t_factor_df['f_rtn'] = t_factor_df['f_rtn'].astype(float)
        t_factor_df['factor'] = t_factor_df['factor'].astype(float)

        factor_ic.append(
            {
                'datetime': dt,
                'ic': t_factor_df['f_rtn'].corr(t_factor_df['factor'])
            }
        )
    factor_ic_df = pd.DataFrame(factor_ic)
    factor_ic_df['%s_expanding_ic' % factor] = factor_ic_df['ic'].expanding().sum()
    factor_ic_df.to_csv(os.path.join(r'D:\commodity\data\hf_ic', '%s.csv' % factor))

