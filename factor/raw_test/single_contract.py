import pandas as pd
import os
import matplotlib.pyplot as plt

pd.set_option('expand_frame_repr', False)


def f1(x):
    x['rtn'] = x['close'] / x['open'] - 1
    res.append(
        {
            'date': x['datetime'].iloc[0],
            'vol': x['rtn'].std(ddof=1)
        }
    )


data_path = 'D:\\futures_data\\'
commodity = 'FG'
contract = 'FG2105'

data = pd.read_csv(os.path.join(data_path, commodity, '%s.csv' % contract))
data = data[['datetime', 'open', 'high', 'low', 'close', 'volume', 'open_interest', 'total_turnover']]
data['datetime'] = pd.to_datetime(data['datetime'])


data_h = data.resample(rule='1H', on='datetime').agg(
    {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum',
        'open_interest': 'last',
        'total_turnover': 'sum'
    }
)

data_h.reset_index(inplace=True)
data_h.dropna(axis=0, subset=['open'], inplace=True)
data_h['rtn'] = data_h['close'] / data_h['open'] - 1
data_h = data_h[['datetime', 'rtn']]

res = []

data['ymdh'] = data['datetime'].apply(lambda x: x.strftime('%Y-%m-%d %H'))
data.groupby('ymdh').filter(f1)


res_df = pd.DataFrame(res)
print(res_df)

