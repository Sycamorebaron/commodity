import os
from matplotlib import pyplot as plt
import pandas as pd
import statsmodels.api as sm
from utils.base_para import *
pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', 2000)

def form_factor_data(comm, factor_data_path):
    print('FORM FACTOR...')
    factor_list = []
    for roots, dirs, files in os.walk(factor_data_path):
        if files:
            factor_list = files

    sum_data = pd.DataFrame()
    for f in factor_list:
        print(f)
        data = pd.read_excel(os.path.join(factor_data_path, f))
        if comm in data.columns:
            data = data[['date', comm]].copy()
            data.columns = ['date', f.split('.')[0]]
            if len(sum_data):
                sum_data = sum_data.merge(data, on='date', how='outer')
            else:
                sum_data = data
    return sum_data

rtn = 'f5_rtn'
min_len = 100
abort_factor = ['long_member_top10', 'long_member_top20', 'short_member_top10', 'short_member_top20']

rtn_data = pd.read_excel(os.path.join(OUTPUT_DATA_PATH, '%s.xlsx' % rtn))
for comm_info in NORMAL_CONTRACT_INFO[4:]:
    comm = comm_info['id']
    print(comm)
    if comm not in rtn_data:
        continue
    comm_rtn_data = rtn_data[['date', comm]].copy()
    comm_rtn_data.columns = ['date', rtn]
    comm_factor_data = form_factor_data(comm=comm, factor_data_path=local_factor_data_path)
    for abort in abort_factor:
        if abort in comm_factor_data.columns:
            comm_factor_data.drop(labels=[abort], axis=1, inplace=True)

    comm_data = comm_rtn_data.merge(comm_factor_data, on='date', how='outer')
    comm_data.dropna(subset=[rtn], how='any', inplace=True)
    comm_data = comm_data[5:]
    comm_data.reset_index(drop=True, inplace=True)
    comm_data.fillna(method='ffill', inplace=True)
    comm_data.to_csv('test.csv')

    fore_res =[]
    for i in range(min_len, len(comm_data)-2):
        test_data = comm_data[i - min_len: i].copy()
        test_data.reset_index(drop=True, inplace=True)
        forecast_data = comm_data.iloc[i + 1]

        model = sm.regression.linear_model.OLS(endog=test_data[rtn], exog=test_data[test_data.columns[2:]])
        res = model.fit_regularized(method='sqrt_lasso', alpha=0.5)
        test_data['fitted'] = res.fittedvalues

        predict_res = res.predict(exog=list(forecast_data[2:]))[0]
        fore_res.append(
            {
                'date': list(forecast_data)[0],
                rtn: list(forecast_data)[1],
                'res': predict_res
            }
        )
        print(fore_res[-1])
    fore_res_df = pd.DataFrame(fore_res)
    fore_res_df.to_csv('%s_fore_res_df.csv' % comm)