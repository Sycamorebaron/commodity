import pandas as pd
from matplotlib import pyplot as plt

pd.set_option('expand_frame_repr', False)
start_time = pd.to_datetime('2012-12-03')
end_time = pd.to_datetime('2013-01-28')
contract = 'FG1305'

def seg_summary(data, factor, target, segs=10):
    res = []
    for i in range(segs):
        if i == 0:
            seg_data = data.loc[data[factor] <= data[factor].quantile((i + 1) / segs)]
        else:
            seg_data = data.loc[
                (data[factor] > data[factor].quantile(i / segs)) &
                (data[factor] <= data[factor].quantile((i + 1) / segs))
            ]
        res.append(
            {
                'factor_mean': seg_data[factor].mean(),
                '%s_mean' % target: seg_data[target].mean()
            }
        )
    res_df = pd.DataFrame(res)
    print(res_df)
    plt.title('%s : %s' % (factor, target))
    plt.scatter(res_df['factor_mean'], res_df['%s_mean' % target])
    plt.show()


data = pd.read_csv(r'C:\futures_data\FG\FG1305.csv')
data['datetime'] = pd.to_datetime(data['datetime'])
data = data.loc[(data['datetime'] >= pd.to_datetime(start_time)) & (data['datetime'] <= pd.to_datetime(end_time))]
data = data[['datetime', 'open', 'high', 'low', 'close']]
data = data.resample(on='datetime', rule='15T').agg(
    {
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
    }
)
data['range_pct'] = data['high'] / data['low'] - 1
data['c2h'] = data['high'] / data['open'] - 1
data['c2l'] = data['low'] / data['open'] - 1
data['f_c2h'] = data['c2h'].shift(-1)
data['f_c2l'] = data['c2l'].shift(-1)

seg_summary(data=data, factor='range_pct', target='f_c2l', segs=20)