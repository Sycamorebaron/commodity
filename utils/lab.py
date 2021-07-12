import pandas as pd
import os
import numpy as np
from matplotlib import pyplot as plt

pd.set_option('expand_frame_repr', False)

# data_path = r'D:\commodity\data\hf_ic_15t'
#
# files = []
# for roots, dirs, files in os.walk(data_path):
#     if files:
#         break
#
# ic_df = pd.DataFrame()
# for f in files:
#     data = pd.read_csv(os.path.join(data_path, f))
#     data = data[['datetime', 'ic']]
#     data.columns = ['datetime', f.split('.')[0][3:-7]]
#
#     if len(ic_df):
#         ic_df = ic_df.merge(data, on='datetime', how='outer')
#     else:
#         ic_df = data
#
# ic_df = ic_df[ic_df.columns[1:]]
# corr_df = ic_df.corr(method='pearson')
# corr_df.to_excel(r'C:\Users\sycam\Desktop\corr.xlsx', sheet_name='pearson')
# # corr_df = ic_df.corr(method='spearman')
# # corr_df.to_excel(r'C:\Users\sycam\Desktop\corr.xlsx', sheet_name='spearman')

# data = pd.read_csv(r'D:\commodity\data\output\5THFFactor\5Thf_rtn2011-01-01_2021-02-28.csv')
# data = pd.read_csv(r'D:\commodity\data\output\15THFFactor\15Thf_rtn.csv')

# data = data[[
#     'datetime', 'L', 'C', 'M', 'RU', 'SR', 'A', 'AL', 'P', 'ZN', 'V', 'CF', 'RO', 'RB', 'ER', 'CU', 'AU', 'Y', 'TA',
#     'PB', 'J', 'ME', 'AG', 'OI', 'FG', 'RM', 'JM', 'TC', 'BU', 'I', 'JD', 'FB', 'PP', 'HC', 'MA', 'SF', 'SM', 'CS',
#     'SN', 'NI', 'ZC', 'CY', 'AP', 'SC', 'SP', 'EG', 'CJ', 'UR', 'NR', 'SS', 'EB', 'SA', 'PG', 'LU', 'PF', 'BC', 'LH',
#     'PK'
# ]].copy()
# data['datetime'] = pd.to_datetime(data['datetime'])
# ic_res = []
# for i in range(2, len(data)):
#     t_data = data[i - 2: i].T
#     t_data = t_data.dropna(how='any')
#     t_data.columns = ['last', 'now']
#     now_dt = t_data['now'].iloc[0]
#     t_data = t_data.loc[t_data.index != 'datetime'].copy()
#     t_data['now'] = t_data['now'].astype(float)
#     t_data['last'] = t_data['last'].astype(float)
#     print(now_dt)
#     ic_res.append(
#         {
#             'now_dt': now_dt,
#             'ic': t_data['now'].corr(t_data['last']),
#         }
#     )
# ic_df = pd.DataFrame(ic_res)
# ic_df['exp_ic'] = ic_df['ic'].expanding().sum()
# ic_df = ic_df.resample(rule='1D', on='now_dt').agg(
#     {
#         'ic': 'last',
#         'exp_ic': 'last'
#     }
# )
#
# print(ic_df)
# ic_df.to_csv(r'C:\Users\sycam\Desktop\ic_df.csv')



# data['tm'] = data['datetime'].apply(lambda x: x.strftime('%H:%M'))
# tm_list = list(data['tm'].drop_duplicates())
#
# for tm in tm_list:
#     tm_res = []
#     for comm in data.columns[1:-1]:
#         comm_d = data[['datetime', comm, 'tm']].copy()
#
#         comm_res = {'comm': comm}
#         for order in range(1, 10):
#             print(comm, order)
#             comm_d['hist_rtn'] = comm_d[comm].shift(order)
#             comm_d['_tm'] = comm_d['tm'].shift(order)
#
#             comm_d_tm = comm_d.loc[comm_d['_tm'] == tm]
#             if len(comm_d_tm) > 100:
#                 comm_res['%s_order' % order] = comm_d_tm['hist_rtn'].corr(comm_d_tm[comm])
#         tm_res.append(comm_res)
#
#     tm_res_df = pd.DataFrame(tm_res)
#     tm_res_df.set_index('comm', inplace=True)
#
#     plt.figure(figsize=[20, 10])
#
#     for i in range(len(tm_res_df)):
#
#         plt.bar(x=[l + 1/(len(tm_res_df)) * 0.9*i for l in range(9)], height=tm_res_df.iloc[i].values, width=0.01)
#
#     plt.title(tm)
#
#     plt.savefig(r'C:\Users\sycam\Desktop\order\%s.png' % (tm.split(':')[0] + tm.split(':')[1]))
#     plt.close()
#

close_data = pd.read_csv(r'C:\5t_factor\5Thf_rtn.csv')
high_data = pd.read_csv(r'C:\5t_factor\5Thighest_rtn.csv')
low_data = pd.read_csv(r'C:\5t_factor\5Tlowest_rtn.csv')

comm_list = [
    'L', 'C', 'M', 'RU', 'SR', 'A', 'AL', 'P', 'ZN', 'V', 'CF', 'RO', 'RB', 'ER', 'CU', 'AU', 'Y', 'TA', 'PB', 'J',
    'ME', 'AG', 'OI', 'FG', 'RM', 'JM', 'TC', 'BU', 'I', 'JD', 'FB', 'PP', 'HC', 'MA', 'SF', 'SM', 'CS', 'SN', 'NI',
    'ZC', 'CY', 'AP', 'SC', 'SP', 'EG', 'CJ', 'UR', 'NR', 'SS', 'EB', 'SA', 'PG', 'LU', 'PF', 'BC', 'LH', 'PK'
]

res = []
for comm in comm_list:
    normal = close_data[['datetime', comm]]
    normal.columns = ['datetime', 'normal']

    high = high_data[['datetime', comm]]
    high.columns = ['datetime', 'high']

    low = low_data[['datetime', comm]]
    low.columns = ['datetime', 'low']

    data = normal.merge(high, on='datetime', how='outer')
    data = data.merge(low, on='datetime', how='outer')

    data.dropna(subset=['normal', 'high', 'low'], how='any', inplace=True)
    data['f_rtn'] = data['normal'].shift(-1)
    data['f_high'] = data['high'].shift(-1)
    data['f_low'] = data['low'].shift(-1)

    data['normal'] = data['normal'].astype(float)
    data['f_rtn'] = data['f_rtn'].astype(float)
    data['f_high'] = data['f_high'].astype(float)
    data['f_low'] = data['f_low'].astype(float)

    res.append(
        {
            'comm': comm,
            'self_corr': data['normal'].corr(data['f_rtn']),
            'high_corr': data['normal'].corr(data['f_high']),
            'high_self_corr': data['high'].corr(data['f_high']),
            'low_self_corr': data['low'].corr(data['f_low']),
            'low_corr': data['normal'].corr(data['f_low']),
        }
    )
res_df = pd.DataFrame(res)
res_df.to_csv(r'C:\Users\sycam\Desktop\high_low_corr.csv')
