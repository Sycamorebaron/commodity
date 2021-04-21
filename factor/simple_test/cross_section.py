import pandas as pd
import os
from matplotlib import pyplot as plt

pd.set_option('expand_frame_repr', False)

data_path = r'D:\commodity\data\output'
factor = 'rtn_skew'
rtn = 'f5_rtn'

factor_data = pd.read_excel(os.path.join(data_path, '%s.xlsx' % factor))
factor_data = factor_data[factor_data.columns[1:]]
rtn_data = pd.read_excel(os.path.join(data_path, '%s.xlsx' % rtn))
rtn_data = rtn_data[rtn_data.columns[1:]]
_date_list = list(rtn_data['date'])
date_list = list(factor_data['date'])

cs_ic_res = []
for date in date_list:
    if date not in _date_list:
        continue
    print(date)
    t_factor = factor_data.loc[factor_data['date'] == date].T.reset_index()[1:]
    t_factor.columns = ['comm', 'factor']
    t_rtn = rtn_data.loc[rtn_data['date'] == date].T.reset_index()[1:]
    t_rtn.columns = ['comm', 'f_rtn']
    t_data = t_factor.merge(t_rtn, on='comm', how='inner')
    t_data.dropna(inplace=True, axis=0, how='any')

    if len(t_data):
        t_data[['factor', 'f_rtn']] = t_data[['factor', 'f_rtn']].astype(float)

        cs_ic_res.append(
            {
                'date': date,
                'cs_ic': t_data['factor'].corr(t_data['f_rtn'])
            }
        )
cs_ic_df = pd.DataFrame(cs_ic_res)
cs_ic_df['cum'] = cs_ic_df['cs_ic'].expanding().sum()
cs_ic_df.set_index('date', inplace=True)
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.plot(cs_ic_df['cs_ic'], color='blue')
ax2 = ax.twinx()
ax2.plot(cs_ic_df['cum'], color='red')

plt.show()


