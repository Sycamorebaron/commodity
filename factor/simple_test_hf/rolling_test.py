import pandas as pd
import os
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestRegressor
pd.set_option('expand_frame_repr', False)


def get_data(comm, data_path=r'D:\commodity\data\hf_comm_factor'):
    data = pd.read_csv(os.path.join(data_path, '%s.csv' % comm))
    data['datetime'] = pd.to_datetime(data['datetime'])
    data['f_rtn'] = data['rtn'].shift(-1)
    data = data[1:].copy()

    not_close_cond = data['datetime'].apply(lambda x: x.strftime('%H:%M') != '14:30')
    data = data.loc[not_close_cond].copy()

    data.reset_index(drop=True, inplace=True)
    return data


def train_model(data, factors, target='f_rtn'):

    model_st = RandomForestRegressor()
    model_st.fit(X=data[factors], y=data[target])
    return model_st


def predict(model, data, factors):
    res = model.predict(X=[list(data[factors])])[0]
    return res


def rolling(comm, data, factors, length=100, target='f_rtn'):
    res = []
    for i in range(length, len(data) - 1):
        t_data = data[i - length: i].copy()
        t_data.dropna(how='any', inplace=True)
        if len(t_data):
            next_data = data.iloc[i].copy()
            next_data.dropna(inplace=True)
            t_factors = [i for i in factors if i in list(next_data.index)]

            model = train_model(data=t_data, factors=t_factors, target=target)
            pred_res = predict(model=model, data=next_data, factors=t_factors)
            real_res = next_data[target]
            res.append(
                {
                    'datetime': t_data['datetime'].iloc[-1],
                    'pred_res': pred_res,
                    'real_res': real_res,
                }
            )
        if len(res):
            print(comm, res[-1])

    return pd.DataFrame(res)


def comm_test(comm):
    _factors = [
        'abig_ra_corr', 'abig_rtn_mean', 'abig_rtn_vol', 'doi_rtn_corr', 'dvol_doi_corr', 'dvol_rtn_corr',
        'd_first_com', 'd_first_com_std', 'd_sec_com', 'd_sec_com_std', 'first_com_range', 'first_explained_ratio',
        'kurt', 'mean', 'sec_com_range', 'sec_explained_ratio', 'skew', 'std', 'vbig_rtn_mean', 'vbig_rtn_vol',
        'vbig_rv_corr', 'nine', 'nine_half', 'ten', 'ten_half', 'eleven', 'one', 'one_half', 'two'
    ]
    _data = get_data(comm=comm)
    predict_df = rolling(comm=comm, data=_data, factors=_factors)
    plt.scatter(predict_df['pred_res'], predict_df['real_res'])
    plt.show()
    # predict_df.to_csv(os.path.join(r'D:\commodity\data\hf_test_res', '%s_test_res.csv' % comm))


def batch_test(comm_list):
    for comm in comm_list:
        comm_test(comm=comm)


if __name__ == '__main__':

    comm_test('SA')

    # 集体测试
    # comm_list = []
    # for roots, dirs, files in os.walk(r'D:\commodity\data\hf_comm_factor'):
    #     if files:
    #         comm_list = [i.split('.')[0] for i in files]
    #         break
    # local_list = []
    # for roots, dirs, files in os.walk(r'D:\commodity\data\hf_test_res'):
    #     if files:
    #         local_list = [i.split('_')[0] for i in files]
    #         break
    #
    # comm_list_1 = comm_list[:14]
    # comm_list_2 = comm_list[14:28]
    # comm_list_3 = comm_list[28:43]
    # comm_list_4 = comm_list[43:]
    #
    # pool = Pool(processes=4)
    # pool.apply_async(batch_test, (comm_list_1,))
    # pool.apply_async(batch_test, (comm_list_2,))
    # pool.apply_async(batch_test, (comm_list_3,))
    # pool.apply_async(batch_test, (comm_list_4,))
    #
    # pool.close()
    # pool.join()
