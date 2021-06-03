import pandas as pd
import os

pd.set_option('expand_frame_repr', False)

data_path = r'D:\commodity\data\hf_comm_factor_15t'

# factor_list = [
#     'abig_ra_corr', 'abig_rtn_mean', 'abig_rtn_vol', 'doi_rtn_corr', 'dvol_doi_corr', 'dvol_rtn_corr',
#     'd_first_com', 'd_first_com_std', 'd_oi', 'd_sec_com', 'd_sec_com_std', 'first_com_range', 'first_explained_ratio',
#     'highest_rtn', 'kurt', 'lowest_rtn', 'mean', 'P0V1', 'P0V2', 'P0V3', 'P1V0', 'P2V0', 'P3V0', 'R0DV1', 'R0DV2',
#     'R0DV3', 'R1DV0', 'R2DV0', 'R3DV0', 'range_pct', 'sec_com_range', 'sec_explained_ratio', 'skew', 'std',
#     'vbig_rtn_mean', 'vbig_rtn_vol', 'vbig_rv_corr', 'vol_oi'
#     # 'mean'
# ]

factor_list = [
    '15Tabig_ra_corr', '15Tabig_rtn_mean', '15Tabig_rtn_vol', '15Tamihud', '15Tdoi_rtn_corr', '15Tdown_move_vol_pct',
    '15Tdown_rtn_mean', '15Tdown_rtn_std', '15Tdvol_doi_corr', '15Tdvol_rtn_corr', '15Td_oi', '15Thf_rtn',
    '15Thighest_rtn', '15Tkurt', '15TLOT', '15Tlowest_rtn', '15Tmean', '15TP0V1', '15TP0V2', '15TP0V3', '15TP1V0',
    '15TP2V0', '15TP3V0', '15Tpastor_gamma', '15TR0DV1', '15TR0DV2', '15TR0DV3', '15TR1DV0', '15TR2DV0', '15TR3DV0',
    '15Trange_pct', '15Troll_spread', '15Tskew', '15Tstd', '15Ttrend_ratio', '15Tup_move_vol_pct', '15Tup_rtn_mean',
    '15Tup_rtn_std', '15Tup_vol_pct', '15Tvbig_rtn_mean', '15Tvbig_rtn_vol', '15Tvbig_rv_corr', '15Tvol_oi'
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
        print(comm)
        data = pd.read_csv(os.path.join(data_path, comm))
        data.sort_values(by='datetime', ascending=True, inplace=True)
        data.reset_index(drop=True, inplace=True)

        data['%s_f_rtn' % comm] = data['rtn'].shift(-1)
        data = data[['datetime', factor, '%s_f_rtn' % comm]].copy()
        data.columns = ['datetime', comm.split('.')[0], '%s_f_rtn' % comm.split('.')[0]]
        data['datetime'] = pd.to_datetime(data['datetime'])
        if len(factor_sum_data):
            factor_sum_data = factor_sum_data.merge(data, on='datetime', how='outer')
        else:
            factor_sum_data = data
        factor_sum_data.drop_duplicates(subset=['datetime'], inplace=True)
        factor_sum_data.reset_index(drop=True, inplace=True)
        print(factor_sum_data.size)
    factor_sum_data.sort_values(by='datetime', ascending=True, inplace=True)
    factor_sum_data.reset_index(drop=True, inplace=True)

    for i in range(len(factor_sum_data) - 1):
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
        t_factor_df.sort_values(by='factor', inplace=True, ascending=True)
        t_factor_df.reset_index(drop=True, inplace=True)
        if len(t_factor_df):
            factor_ic.append(
                {
                    'datetime': dt,
                    'ic': t_factor_df['f_rtn'].corr(t_factor_df['factor']),
                    'top': t_factor_df['comm'].iloc[-1],
                    'top_rtn': t_factor_df['factor'].iloc[-1],
                    'top_f_rtn': t_factor_df['f_rtn'].iloc[-1],
                    'bot': t_factor_df['comm'].iloc[0],
                    'bot_rtn': t_factor_df['factor'].iloc[0],
                    'bot_f_rtn': t_factor_df['f_rtn'].iloc[0],
                }
            )
    factor_ic_df = pd.DataFrame(factor_ic)
    factor_ic_df['%s_expanding_ic' % factor] = factor_ic_df['ic'].expanding().sum()
    factor_ic_df.to_csv(os.path.join(r'D:\commodity\data\hf_ic_15t', '%s_detail.csv' % factor))
