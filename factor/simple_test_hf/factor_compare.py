import pandas as pd
import os

pd.set_option('expand_frame_repr', False)

data_path = r'D:\commodity\data\hf_ic'

factors = []
for roots, dirs, files in os.walk(data_path):
    if files:
        factors = [i for i in files if i.endswith('detail.csv')]

sum_data = pd.DataFrame()
for f in factors:
    data = pd.read_csv(os.path.join(data_path, f))
    data['datetime'] = pd.to_datetime(data['datetime'])
    data = data[['datetime', '%s_expanding_ic' % f[:-11]]]
    data.columns = ['datetime', f[:-11]]
    data = data.resample(on='datetime', rule='1d').agg(
        {
            f[:-11]: 'last'
        }
    )
    data.reset_index(inplace=True)
    if len(sum_data):
        sum_data = sum_data.merge(data, on='datetime', how='outer')
    else:
        sum_data = data
sum_data.dropna(subset=list(sum_data.columns[1:]), how='all', inplace=True)
sum_data.to_excel(r'D:\commodity\data\factor_compare.xlsx')

