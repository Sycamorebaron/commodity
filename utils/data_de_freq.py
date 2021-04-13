import pandas as pd
import os

pd.set_option('expand_frame_repr', False)

data_path = r'C:\futures_data'
target_path = r'C:\futures_data_5T'

for roots, dirs, files in os.walk(data_path):
    if files:
        for f in files:
            d_path = os.path.join(roots, f)
            if not os.path.exists(os.path.join(target_path, roots.split('\\')[-1])):
                os.makedirs(os.path.join(target_path, roots.split('\\')[-1]))
            if roots.split('\\')[-1] == 'public':
                continue
            else:
                if f.endswith('open_interest.csv'):
                    os.system('copy %s %s' % (os.path.join(roots, f), os.path.join(target_path, roots.split('\\')[-1], f)))
                else:
                    data = pd.read_csv(os.path.join(roots, f))
                    if not len(data):
                        pd.DataFrame().to_csv(os.path.join(target_path, roots.split('\\')[-1], f))
                        print(f)
                    else:
                        data = data[[
                            'order_book_id', 'datetime', 'open', 'high', 'low', 'close', 'volume', 'open_interest',
                            'total_turnover'
                        ]]
                        data['datetime'] = pd.to_datetime(data['datetime'])
                        data = data.resample(rule='5T', on='datetime').agg(
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
                        data.dropna(subset=['open'], how='any', inplace=True)
                        data.to_csv(os.path.join(target_path, roots.split('\\')[-1], f))
                        print(f)