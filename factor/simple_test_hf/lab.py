import pandas as pd
pd.set_option('expand_frame_repr', False)

_rtn_data = pd.read_csv(r'C:\30t_factor\hf_rtn.csv')
rtn_data = _rtn_data[[
    'L', 'C', 'M', 'RU', 'SR', 'A', 'AL', 'P', 'ZN', 'V', 'B', 'CF', 'RO', 'RB', 'ER', 'CU', 'AU', 'Y', 'TA', 'PB', 'J',
    'ME', 'AG', 'OI', 'FG', 'RM', 'JM', 'TC', 'BU', 'I', 'JD', 'FB', 'PP', 'HC', 'MA', 'SF', 'SM', 'CS', 'SN', 'NI',
    'ZC', 'CY', 'AP', 'SC', 'SP', 'EG', 'CJ', 'UR', 'NR', 'SS', 'EB', 'SA', 'PG', 'LU', 'PF', 'BC', 'LH', 'PK'
]].copy()

res = []
for i in range(1, len(rtn_data)):
    if pd.to_datetime(_rtn_data['datetime'].iloc[i]).strftime('%H') in ['01', '02', '00', '21', '22', '23']:
        continue

    t_data = rtn_data[i-1: i+1].T.copy()
    t_data.dropna(subset=[i-1, i], how='any', inplace=True)
    corr = t_data[i-1].corr(t_data[i])
    res.append(
        {
            'datetime': _rtn_data['datetime'].iloc[i],
            'ic': corr,
            'num': len(t_data)
        }
    )
    print(res[-1])
res_df = pd.DataFrame(res)
res_df['exp_ic'] = res_df['ic'].expanding().sum()
res_df.to_csv(r'C:\Users\sycam\Desktop\rtn.csv')
