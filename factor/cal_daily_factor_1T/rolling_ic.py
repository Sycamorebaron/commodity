import pandas as pd
import os

pd.set_option('expand_frame_repr', False)
# data_path = r'D:\commodity\data\output\1DHFfactor'
#
# for roots, dirs, files in os.walk(data_path):
#     if files:
#         print([i.split('.')[0] for i in files])
#         exit()
def cal_ic():
    data_path = r'D:\commodity\data\output\1DHFfactor'

    factor_list = [
        '1dabig_ra_corr', '1dabig_rtn_mean', '1dabig_rtn_vol', '1damihud', '1dbollerslev_RSJ', '1dBV', '1dBV_rtn',
        '1dBV_sigma', '1dclose_15t_pct', '1dclose_30t_pct', '1dclose_5t_pct', '1ddoi_rtn_corr', '1ddown_move_vol_pct',
        '1ddown_rtn_mean', '1ddown_rtn_std', '1ddown_vol_pct', '1ddvol_doi_corr', '1ddvol_rtn_corr', '1dd_first_com',
        '1dd_first_com_std', '1dd_oi', '1dd_sec_com', '1dd_sec_com_std', '1dfirst_com_range', '1dfirst_explained_ratio',
        '1dhf_rtn', '1dhighest_rtn', '1dkurt', '1dLOT', '1dlowest_rtn', '1dmax_rtn', '1dmean', '1dmin_rtn',
        '1dopen_15t_pct', '1dopen_30t_pct', '1dopen_5t_pct', '1dP0V1', '1dP0V2', '1dP0V3', '1dP1V0', '1dP2V0', '1dP3V0',
        '1dpastor_gamma', '1dR0DV1', '1dR0DV2', '1dR0DV3', '1dR1DV0', '1dR2DV0', '1dR3DV0', '1drange_pct',
        '1droll_spread', '1dsec_com_range', '1dsec_explained_ratio', '1dskew', '1dstd', '1dstd_rtn', '1dtrend_ratio',
        '1dup_move_vol_pct', '1dup_rtn_mean', '1dup_vol_pct', '1dvbig_rtn_mean', '1dvbig_rtn_vol', '1dvbig_rv_corr',
        '1dvol_oi'
    ]

    rtn = '1dhf_rtn'
    rtn_data = pd.read_csv(os.path.join(data_path, '%s.csv' % rtn))
    rtn_data = rtn_data[[i for i in rtn_data.columns if not i.startswith('Unnamed')]]
    for col in [i for i in rtn_data.columns if i != 'datetime']:
        rtn_data[col] = rtn_data[col].shift(-1)


    for factor in factor_list:
        factor_data = pd.read_csv(os.path.join(data_path, '%s.csv' % factor))
        factor_data = factor_data[[i for i in rtn_data.columns if not i.startswith('Unnamed')]]
        factor_sum_data = rtn_data.merge(factor_data, on='datetime', suffixes=['_f_rtn', ''], how='outer')

        factor_ic = []
        for i in range(len(factor_sum_data) - 1):
            dt = factor_sum_data['datetime'].iloc[i]
            print(factor, dt)
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
        # factor_ic_df.to_csv(os.path.join(r'C:\Users\sycam\Desktop', 'all_%s_detail.csv' % factor))
        # exit()
        factor_ic_df.to_csv(os.path.join(r'D:\commodity\data\hf_ic_1d', '%s_detail.csv' % factor))


def draw():

    ic_path = r'D:\commodity\data\hf_ic_1d'
    files = []
    for roots, dirs, files in os.walk(ic_path):
        if files:
            break
    sum_ic = pd.DataFrame()
    for f in files:
        d = pd.read_csv(os.path.join(ic_path, f))
        d = d[['datetime', '%s_expanding_ic' % f.split('.')[0][:-7]]]
        d.columns = ['datetime', f.split('.')[0][:-7]]

        if len(sum_ic):
            sum_ic = sum_ic.merge(d, on='datetime', how='outer')
        else:
            sum_ic = d
    sum_ic.to_csv(r'D:\commodity\data\1d_exp_ic.csv')


if __name__ == '__main__':
    cal_ic()
    draw()