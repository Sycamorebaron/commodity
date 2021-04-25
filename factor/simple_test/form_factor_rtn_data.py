import pandas as pd
import os
from utils.base_para import COMM_FACTOR_DATA_PATH, local_factor_data_path, NORMAL_CONTRACT_INFO

pd.set_option('expand_frame_repr', False)


def form_factor_data(factor_data_path):
    factor_dict = {}
    print('READ FACTOR...')
    factor_list = []
    for roots, dirs, files in os.walk(factor_data_path):
        if files:
            factor_list = files

    for f in factor_list:
        print(f)
        data = pd.read_excel(os.path.join(factor_data_path, f))
        factor_dict[f.split('.')[0]] = data
    return factor_dict

def form_comm_data(comm, factor_dict):
    print(comm)
    sum_data = pd.DataFrame()
    for factor in factor_dict.keys():
        data = factor_dict[factor]
        if comm in data.columns:
            data = data[['date', comm]].copy()
            data.columns = ['date', factor]
            if len(sum_data):
                sum_data = sum_data.merge(data, on='date', how='outer')
            else:
                sum_data = data
    return sum_data



if __name__ == '__main__':
    factor_dict = form_factor_data(factor_data_path=local_factor_data_path)
    for comm_info in NORMAL_CONTRACT_INFO:

        commodity = comm_info['id']

        comm_factor_data = form_comm_data(comm=commodity, factor_dict=factor_dict)
        comm_factor_data['date'] = pd.to_datetime(comm_factor_data['date'])

        self_date_cond = (comm_factor_data['date'] >= pd.to_datetime(comm_info['first_listed_date'])) & \
                    (comm_factor_data['date'] < pd.to_datetime(comm_info['last_de_listed_date']))
        data_date_cond = (comm_factor_data['date'] >= pd.to_datetime('2010-01-01')) & \
                         (comm_factor_data['date'] < pd.to_datetime('2021-02-26'))

        comm_factor_data = comm_factor_data.loc[self_date_cond & data_date_cond]

        comm_factor_data.sort_values(by='date', inplace=True)
        comm_factor_data.reset_index(drop=True, inplace=True)

        comm_factor_data.to_csv(os.path.join(COMM_FACTOR_DATA_PATH, '%s.csv' % commodity))
