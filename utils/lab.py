import pandas as pd
from sklearn.decomposition import PCA
pd.set_option('expand_frame_repr', False)

data = pd.read_csv(r'C:\futures_data_5T\M\M1401.csv')
data['datetime'] = pd.to_datetime(data['datetime'])
data = data.loc[data['datetime'].apply(lambda x: x.strftime('%Y-%m-%d') == '2013-01-18')]

data = data[['open', 'high', 'low', 'close', 'volume', 'open_interest', 'total_turnover']]
for col in ['open', 'high', 'low', 'close', 'volume', 'open_interest', 'total_turnover']:
    data[col] = (data[col] - data[col].mean()) / data[col].std(ddof=1)

print(data)
pca = PCA(n_components=3)
new_x = pca.fit_transform(data)
com_df = pd.DataFrame(new_x)
print(com_df)
print(pca.explained_variance_ratio_)

d_first_com = com_df[0].iloc[-1] - com_df[0].iloc[0]
d_sec_com = com_df[1].iloc[-1] - com_df[1].iloc[0]
first_com_range = (com_df[0].max() - com_df[0].min())
sec_com_range = (com_df[1].max() - com_df[1].min())
d_first_com_std = (com_df[0] - com_df[0].shift(1)).std(ddof=1)
d_sec_com_std = (com_df[1] - com_df[1].shift(1)).std(ddof=1)
first_explained_ratio = pca.explained_variance_ratio_[0]
sec_explained_ratio = pca.explained_variance_ratio_[1]

print(
    d_first_com, d_sec_com, first_com_range, sec_com_range, d_first_com_std, d_sec_com_std,
    first_explained_ratio, sec_explained_ratio
)