from hmmlearn import hmm
from sklearn.cluster import KMeans
import warnings
import pandas as pd
import os
from matplotlib import pyplot as plt
warnings.filterwarnings("ignore")
pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', 200)  # 行


def get_factor(comm, local_factor_data_path, begin_date, end_date):
    files = []
    factor_dict = {}
    for roots, dirs, files in os.walk(local_factor_data_path):
        if files:
            break
    print('load factors...')

    for f in files:
        data = pd.read_csv(os.path.join(local_factor_data_path, f))
        data['datetime'] = pd.to_datetime(data['datetime'])
        factor_dict[f.split('.')[0]] = data

    _comm_d = pd.DataFrame()
    for factor in factor_dict.keys():
        _comm_f = factor_dict[factor][['datetime', comm]]
        _comm_f.columns = ['datetime', factor]
        if len(_comm_d):
            _comm_d = _comm_d.merge(_comm_f, on='datetime', how='outer')
        else:
            _comm_d = _comm_f

    _comm_d.sort_values(by='datetime', ascending=True, inplace=True)
    cond1 = _comm_d['datetime'].dt.hour >= 9
    cond2 = _comm_d['datetime'].dt.hour <= 15
    _comm_d = _comm_d.loc[cond1 & cond2]

    _comm_d.reset_index(drop=True, inplace=True)
    _comm_d['15Tf_rtn'] = _comm_d['15Thf_rtn'].shift(-1)
    cond1 = _comm_d['datetime'] >= pd.to_datetime(begin_date)
    cond2 = _comm_d['datetime'] <= pd.to_datetime(end_date)
    _comm_d = _comm_d.loc[cond1 & cond2].reset_index(drop=True)

    return  _comm_d


def kmeans_fillna(data):
    miss_col = []
    for col in [i for i in data.columns if i not in ['datetime', '15Tf_rtn']]:
        if data[col].isnull().any():
            miss_col.append(col)

    use_col = [i for i in data.columns if i not in ['datetime', '15Tf_rtn'] + miss_col]
    for col in miss_col:
        print('fill', col)

        f_data = data[use_col + [col]].copy()
        f_data['ori_index'] = f_data.index

        f_data_fill = f_data.loc[f_data[col].isna()].copy().reset_index(drop=True)
        f_data_train = f_data.loc[f_data[col].notna()].copy().reset_index(drop=True)
        model = KMeans(n_clusters=16, random_state=6)
        model.fit(X=f_data_train[use_col], y=f_data_train[col])

        f_data_train['label'] = model.labels_

        pred_res = model.predict(X=f_data_fill[use_col])
        f_data_fill['label'] = pred_res
        for i in range(len(f_data_fill)):
            l = f_data_fill['label'].iloc[i]
            f_data_fill[col].iloc[i] = f_data_train.loc[f_data_train['label'] == l, col].mean()

        filled = pd.concat([f_data_train, f_data_fill]).sort_values(by='ori_index').reset_index(drop=True)
        data[col] = filled[col]

    return data


def get_factor_list(data):
    col_corr = {}
    for col in [i for i in data.columns if i not in ['datetime', '15Tf_rtn']]:
        col_corr[col] = data[col].corr(data['15Tf_rtn'])
    corr_df = pd.DataFrame(col_corr, index=['corr']).T.abs()
    corr_df.sort_values(by='corr', inplace=True, ascending=False)
    chosen = list(corr_df.index[:int(len(corr_df) / 2)])
    return chosen


def modify_data(train_data, test_data):
    for col in [i for i in train_data.columns if i not in ['datetime', '15Tf_rtn']]:
        train_mean = train_data[col].mean()
        train_std = train_data[col].std(ddof=1)

        train_data[col] -= train_mean
        train_data[col] /= train_std

        test_data[col] -= train_mean
        test_data[col] /= train_std
    return train_data, test_data


def drop_invalid(data):
    invalid_time = ['09:00', '10:30', '13:30']
    data = data.loc[data['datetime'].apply(lambda x: x.strftime('%H:%M') not in invalid_time)]
    data.reset_index(drop=True, inplace=True)
    return data



if __name__ == '__main__':
    l_comm = 'FG'
    l_local_factor_data_path = r'C:\15t_factor'


    full_train_data = get_factor(l_comm, l_local_factor_data_path, begin_date='2020-01-01', end_date='2021-01-01')
    full_train_data = drop_invalid(data=full_train_data)
    full_train_data = kmeans_fillna(data=full_train_data)

    full_test_data = get_factor(l_comm, l_local_factor_data_path, begin_date='2021-01-05', end_date='2021-02-05')
    full_test_data = drop_invalid(data=full_test_data)
    full_test_data = kmeans_fillna(data=full_test_data)

    factor_list = get_factor_list(full_train_data)

    train_data = full_train_data[factor_list + ['15Tf_rtn']].copy()
    test_data = full_test_data[factor_list + ['15Tf_rtn']].copy()

    train_data, test_data = modify_data(train_data=train_data, test_data=test_data)

    remodel = hmm.GaussianHMM(n_components=10, covariance_type="full", n_iter=100)
    remodel.fit(train_data[[i for i in train_data.columns if i not in ['datetime', '15Tf_rtn']]].copy())

    train_data['pred'] = remodel.predict(train_data[[i for i in train_data.columns if i not in ['datetime', '15Tf_rtn']]])

        # plt.scatter(train_data['pred'], train_data['15Tf_rtn'])

        # bar_res = []
        # for i in list(train_data['pred'].drop_duplicates()):
        #     bar_res.append([i, train_data.loc[train_data['pred'] == i, '15Tf_rtn'].mean()])
        #
        # plt.bar(x=[i[0] for i in bar_res], height=[i[1] for i in bar_res], alpha=0.5)
        # plt.title(factor)
        # plt.show()

    bar_res = []
    for i in list(train_data['pred'].drop_duplicates()):
        if len(train_data.loc[train_data['pred'] == i]) > 10:

            bar_res.append([i, train_data.loc[train_data['pred'] == i, '15Tf_rtn'].mean()])
        else:
            bar_res.append([i, 0])

    pred_res = remodel.predict(test_data[[i for i in train_data.columns if i not in ['datetime', '15Tf_rtn', 'pred']]])
    test_data['pred'] = pred_res
    plt.scatter(test_data['pred'], test_data['15Tf_rtn'])
    plt.bar(x=[i[0] for i in bar_res], height=[i[1] for i in bar_res], alpha=0.5)
    plt.show()
