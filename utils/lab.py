import pandas as pd
import os
from statsmodels.tsa.stattools import adfuller
import sklearn.tree as st
from sklearn.decomposition import PCA
from matplotlib import pyplot as plt

pd.set_option('expand_frame_repr', False)

data_path = 'D:\commodity\data\output'
factor_raw_data = pd.read_excel(os.path.join(data_path, 'fg_test_data.xlsx'))
factor_raw_data['date'] = pd.DataFrame(factor_raw_data['date'])

rtn_data = pd.read_excel(os.path.join(data_path, 'f5_rtn.xlsx'))
rtn_data = rtn_data[['date', 'FG']]
rtn_data['date'] = pd.DataFrame(rtn_data['date'])

data = factor_raw_data.merge(rtn_data, on='date', how='inner')
print(data)
data.to_excel(r'C:\Users\sycam\Desktop\fg_test.xlsx')
for col in data.columns[3: -2]:
    t_data = data[[col, 'FG']].copy()
    print(t_data.corr())
    print(t_data.corr().iloc[0, 1])
    exit()

# train_data = raw_data[:1000].copy()
# test_data = raw_data[1000:].copy()
# train_data.reset_index(drop=True, inplace=True)
# test_data.reset_index(drop=True, inplace=True)
#
# data = pd.DataFrame(train_data['date'])
# for col in train_data.columns[2:-1]:
#     data[col] = (train_data[col] - train_data[col].mean()) / train_data[col].std(ddof=1)
# data['f_rtn'] = train_data['f_rtn']
#
#
# stable_data = pd.DataFrame(data['date'])
# for col in data.columns[1:-1]:
#     p_value = adfuller(data[col])[1]
#     if p_value > 0.05:
#         print(col,p_value)
#         stable_data[col] = data[col] - data[col].shift(1)
#     else:
#         stable_data[col] = data[col]
# stable_data['f_rtn']= data['f_rtn']
# stable_data = stable_data[1:]
# stable_data.reset_index(drop=True, inplace=True)
#
# f_rtn_seg = [stable_data['f_rtn'].quantile((i + 1) / 40) for i in range(40)]
#
#
# def f1(x):
#
#     for i in range(len(f_rtn_seg)):
#         if x <= f_rtn_seg[i]:
#             return i
#
#
# stable_data['f_rtn_seg'] = stable_data['f_rtn'].apply(f1)
#
#
# x=stable_data[stable_data.columns[1:-2]]
# y=stable_data['f_rtn_seg']
# model = st.DecisionTreeClassifier(max_depth=5)
# model.fit(X=x, y=y)
# pred_y = model.predict(X=x)
#
# stable_data['fitted_y'] = pd.Series(pred_y)
#
# plt.scatter(x=stable_data['f_rtn_seg'], y=stable_data['fitted_y'])
# plt.show()
#
#
#
#
#
# f_data = pd.DataFrame(test_data['date'])
# for col in test_data.columns[2:-1]:
#     f_data[col] = (test_data[col] - test_data[col].mean()) / test_data[col].std(ddof=1)
# f_data['f_rtn'] = test_data['f_rtn']
# f_stable_data = pd.DataFrame(f_data['date'])
# for col in f_data.columns[1:-1]:
#     p_value = adfuller(f_data[col])[1]
#     if p_value > 0.05:
#         f_stable_data[col] = f_data[col] - f_data[col].shift(1)
#     else:
#         f_stable_data[col] = f_data[col]
# f_stable_data['f_rtn'] = f_data['f_rtn']
# f_stable_data = f_stable_data[1:]
# f_stable_data.reset_index(drop=True, inplace=True)
#
# pred_y = model.predict(X=f_stable_data[f_stable_data.columns[1:-1]])
# f_stable_data['f_predicted'] = pd.Series(pred_y)
#
# plt.scatter(x=f_stable_data['f_rtn'], y=f_stable_data['f_predicted'])
# plt.show()


# future_days = 5
# f_rtn_col = 'f_%sd_rtn' % future_days
#
# raw_data['lable'] = raw_data.index // future_days
# raw_data.drop('f_rtn', inplace=True, axis=1)
#
# features = list(raw_data.columns[2:-1])
# data = raw_data[features + ['lable']].groupby('lable').mean()
# raw_data[f_rtn_col] = \
#     raw_data['rtn'].rolling(future_days).apply(lambda x: (1 + x).cumprod().iloc[-1] - 1)
# data[f_rtn_col] = raw_data[[f_rtn_col, 'lable']].groupby('lable').last()
#
# data = data[1:].copy()
# data.to_csv(r'C:\Users\sycam\Desktop\ts.csv')
# exit()
# for col in features:
#     data[col] = (data[col] - data[col].mean()) / data[col].std(ddof=1)
#
# for col in data.columns[:-1]:
#     print(data[[col, f_rtn_col]].corr())
#
#
# print(data)
# exit()
#
# n_com = 10
# pca = PCA(n_components=n_com)
# new_x = pca.fit_transform(data[features])
# com_df = pd.DataFrame(new_x)
# com_df.columns = ['f_%s' % i for i in range(n_com)]
# features = list(com_df.columns)
# com_df['target'] = data[f_rtn_col]
# data = com_df
#
# data.reset_index(drop=True, inplace=True)
#
# # data
# train_data = data[1:300].copy()
# test_data = data[200:].copy()
#
# train_f_rtn_seg = [train_data['target'].quantile((i + 1) / 5) for i in range(5)]
#
# def f1(x):
#
#     for i in range(len(train_f_rtn_seg)):
#         if x <= train_f_rtn_seg[i]:
#             return i
#
#
# x = train_data[features].copy()
# y = train_data['target']
#
# model = st.DecisionTreeRegressor(max_depth=5)
# model.fit(X=x, y=y)
# pred_y = model.predict(X=x)
#
# train_data['pred_y'] = pd.Series(pred_y)
# plt.scatter(train_data['target'], train_data['pred_y'])
# plt.show()


