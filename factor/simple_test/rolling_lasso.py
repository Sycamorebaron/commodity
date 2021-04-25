import os
from matplotlib import pyplot as plt
import pandas as pd
import sklearn.tree as st
import statsmodels.api as sm
from sklearn.ensemble import RandomForestRegressor
from utils.base_para import *
pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', 2000)

def form_factor_data():
    data_dict = {}
    print('FORM FACTOR...')
    factor_list = []
    for roots, dirs, files in os.walk(local_factor_data_path):
        if files:
            factor_list = files


    for f in factor_list:
        print(f)
        data = pd.read_excel(os.path.join(local_factor_data_path, f))
        data_dict[f.split('.')[0]] = data

    return data_dict


def form_comm_factor_data(comm, factor_data_dict):
    print('FORM %s FACTOR...' % comm)
    sum_data = pd.DataFrame()
    for factor in factor_data_dict.keys():
        data = factor_data_dict[factor]
        if comm in data.columns:
            data = data[['date', comm]].copy()
            data.columns = ['date', factor]
            if len(sum_data):
                sum_data = sum_data.merge(data, on='date', how='outer')
            else:
                sum_data = data
    return sum_data


if __name__ == '__main__':

    rtn = 'f3_rtn'
    min_len = 100
    abort_factor = ['long_member_top10', 'long_member_top20', 'short_member_top10', 'short_member_top20']
    factor_data_dict = form_factor_data()

    rtn_data = pd.read_excel(os.path.join(OUTPUT_DATA_PATH, '%s.xlsx' % rtn))
    for comm_info in NORMAL_CONTRACT_INFO[4:]:
        comm = comm_info['id']
        print(comm)
        if comm not in rtn_data:
            continue
        comm_rtn_data = rtn_data[['date', comm]].copy()
        comm_rtn_data.columns = ['date', rtn]
        comm_factor_data = form_comm_factor_data(comm=comm, factor_data_dict=factor_data_dict)
        for abort in abort_factor:
            if abort in comm_factor_data.columns:
                comm_factor_data.drop(labels=[abort], axis=1, inplace=True)

        comm_data = comm_rtn_data.merge(comm_factor_data, on='date', how='outer')
        comm_data.dropna(subset=[rtn], how='any', inplace=True)
        comm_data = comm_data[5:]
        comm_data.reset_index(drop=True, inplace=True)
        comm_data.fillna(method='ffill', inplace=True)


        fore_res =[]
        for i in range(min_len, len(comm_data)-2):

            t_data = comm_data[i - min_len: i+1].copy()
            t_data.reset_index(drop=True, inplace=True)
            t_data.dropna(how='any', axis=1, inplace=True)
            for col in t_data.columns[2:]:
                t_data[col] = (t_data[col] - t_data[col].mean()) / t_data[col].std(ddof=1)

            test_data = t_data[:-2].copy()
            forecast_data = t_data.iloc[-1].copy()

            model_st = RandomForestRegressor()

            model_st.fit(X=test_data[test_data.columns[2:]], y=test_data[rtn])
            st_predict_res = model_st.predict(X=[list(forecast_data[2:])])[0]

            fore_res.append(
                {
                    'date': list(forecast_data)[0],
                    rtn: list(forecast_data)[1],
                    'res': st_predict_res
                }
            )
            print(fore_res[-1])
        fore_res_df = pd.DataFrame(fore_res)
        fore_res_df.to_csv(os.path.join(r'D:\commodity\factor\simple_test\decision_tree_scatter', '%s.csv' % comm))
        plt.scatter(fore_res_df['res'], fore_res_df[rtn])
        plt.title(comm)
        plt.savefig(os.path.join(r'D:\commodity\factor\simple_test\decision_tree_scatter', '%s.png' % comm))
        plt.close()