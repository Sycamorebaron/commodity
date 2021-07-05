import pandas as pd
import os

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

data = pd.read_csv(r'D:\commodity\data\output\5THFFactor\5Thf_rtn2011-01-01_2021-02-28.csv')
data = data[[
    'datetime', 'L', 'C', 'M', 'RU', 'SR', 'A', 'AL', 'P', 'ZN', 'V', 'CF', 'RO', 'RB', 'ER', 'CU', 'AU', 'Y', 'TA',
    'PB', 'J', 'ME', 'AG', 'OI', 'FG', 'RM', 'JM', 'TC', 'BU', 'I', 'JD', 'FB', 'PP', 'HC', 'MA', 'SF', 'SM', 'CS',
    'SN', 'NI', 'ZC', 'CY', 'AP', 'SC', 'SP', 'EG', 'CJ', 'UR', 'NR', 'SS', 'EB', 'SA', 'PG', 'LU', 'PF', 'BC', 'LH',
    'PK'
]].copy()
data['datetime'] = pd.to_datetime(data['datetime'])
ic_res = []
for i in range(2, len(data)):
# for i in range(2, 100):
    t_data = data[i - 2: i].T
    t_data = t_data.dropna(how='any')
    t_data.columns = ['last', 'now']
    now_dt = t_data['now'].iloc[0]
    t_data = t_data.loc[t_data.index != 'datetime'].copy()
    t_data['now'] = t_data['now'].astype(float)
    t_data['last'] = t_data['last'].astype(float)
    print(now_dt)
    ic_res.append(
        {
            'now_dt': now_dt,
            'ic': t_data['now'].corr(t_data['last']),
        }
    )
ic_df = pd.DataFrame(ic_res)
ic_df['exp_ic'] = ic_df['ic'].expanding().sum()
ic_df = ic_df.resample(rule='1D', on='now_dt').agg(
    {
        'ic': 'last',
        'exp_ic': 'last'
    }
)

print(ic_df)
ic_df.to_csv(r'C:\Users\sycam\Desktop\ic_df.csv')


