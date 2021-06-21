import pandas as pd
import os
pd.set_option('expand_frame_repr', False)

factor = '2014_signal_df'
factor_data_path = r'C:\syn_factor'

rtn = '15Thf_rtn'
rtn_data_path = r'C:\15t_factor'

factor_data = pd.read_csv(os.path.join(factor_data_path, '%s.csv' % factor))
rtn_data = pd.read_csv(os.path.join(rtn_data_path, '%s.csv' % rtn))

rtn_data['now_dt'] = rtn_data['datetime'].shift(1)

res = []
for dt in list(factor_data['now_dt']):
    print(dt)
    t_factor = pd.DataFrame(factor_data.loc[factor_data['now_dt'] == dt].T)[2:].dropna().reset_index()
    t_factor.columns = ['comm', 'factor']
    t_f_rtn = pd.DataFrame(rtn_data.loc[rtn_data['now_dt'] == dt].T)[2:-1].dropna().reset_index()
    t_f_rtn.columns = ['comm', 'f_rtn']

    t_data = t_factor.merge(t_f_rtn, on='comm', how='outer').dropna()
    t_data['f_rtn'] = t_data['f_rtn'].astype(float)
    t_data['factor'] = t_data['factor'].astype(float)
    res.append(
        {
            'dt': dt,
            'max_factor': t_data['factor'].max(),
            'min_factor': t_data['factor'].min(),
            'max_f_rtn': t_data['f_rtn'].max(),
            'min_f_rtn': t_data['f_rtn'].min(),
            'corr': t_data['f_rtn'].corr(t_data['factor'])
        }
    )
res_df = pd.DataFrame(res)
res_df['cum_ic'] = res_df['corr'].expanding().sum()
res_df.to_csv(r'D:\commodity\data\syn_test_ic.csv')
print(res_df)