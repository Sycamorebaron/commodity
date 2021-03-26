import pandas as pd
import os

pd.set_option('expand_frame_repr', False)

local_files = []
for roots, dirs, files in os.walk(r'D:\futures_data'):
    if files:
        local_files = files

for f in local_files:
    if f.startswith('IF'):
        continue
    if f.startswith('IH'):
        continue
    if f.startswith('IC'):
        continue
    if f.startswith('contract_info'):
        continue

    data = pd.read_csv(os.path.join(r'D:\futures_data', f))
    if len(data):
        data = data[[
            'order_book_id','datetime', 'open', 'high', 'low', 'close', 'volume', 'open_interest',
            'total_turnover'
        ]]
        data['datetime'] = pd.to_datetime(data['datetime'])
        data = data.resample(
            rule='1D', on='datetime'
        ).agg(
            {
                'order_book_id': 'last',
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
                'open_interest': 'last',
                'total_turnover': 'sum'
            }
        )
        data.reset_index(inplace=True)
        data.to_csv(os.path.join(r'D:\futures_data1D', f))
        print(f)