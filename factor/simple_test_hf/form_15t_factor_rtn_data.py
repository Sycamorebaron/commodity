import pandas as pd
import os
from utils.base_para import NORMAL_CONTRACT_INFO

local_hf_factor_path = r'C:\15t_factor'
pd.set_option('expand_frame_repr', False)


def form_factor_data(factor_data_path):
    factor_dict = {}
    print('READ FACTOR...')
    factor_list = []
    for roots, dirs, files in os.walk(factor_data_path):
        if files:
            factor_list = files
    factor_list = [i for i in factor_list if not i.startswith('hf_rtn')]

    for f in factor_list:
        print(f)
        data = pd.read_csv(os.path.join(factor_data_path, f))
        factor_dict[f.split('.')[0]] = data
    return factor_dict

def form_comm_data(comm, factor_dict):
    print(comm)
    sum_data = pd.DataFrame()
    for factor in factor_dict.keys():
        data = factor_dict[factor]
        if comm in data.columns:
            data = data[['datetime', comm]].copy()
            data.columns = ['datetime', factor]
            if len(sum_data):
                sum_data = sum_data.merge(data, on='datetime', how='outer')
            else:
                sum_data = data
    return sum_data


if __name__ == '__main__':
    rtn_data = pd.read_csv(os.path.join(local_hf_factor_path, '15Thf_rtn.csv'))
    factor_dict = form_factor_data(factor_data_path=local_hf_factor_path)

    for comm_info in NORMAL_CONTRACT_INFO:

        commodity = comm_info['id']

        comm_factor_data = form_comm_data(comm=commodity, factor_dict=factor_dict)
        comm_factor_data['datetime'] = pd.to_datetime(comm_factor_data['datetime'])

        # self_date_cond = (comm_factor_data['datetime'] >= pd.to_datetime(comm_info['first_listed_date'])) & \
        #             (comm_factor_data['datetime'] < pd.to_datetime(comm_info['last_de_listed_date']))
        # data_date_cond = (comm_factor_data['datetime'] >= pd.to_datetime('2010-01-01')) & \
        #                  (comm_factor_data['datetime'] < pd.to_datetime('2021-02-26'))
        #
        # comm_factor_data = comm_factor_data.loc[self_date_cond & data_date_cond]

        comm_factor_data.sort_values(by='datetime', inplace=True)
        comm_factor_data.reset_index(drop=True, inplace=True)

        comm_rtn_data = rtn_data[['datetime', commodity]].copy()
        comm_rtn_data.columns = ['datetime', 'rtn']
        comm_rtn_data['datetime'] = pd.to_datetime(comm_rtn_data['datetime'])

        comm_factor_data = comm_rtn_data.merge(comm_factor_data, on='datetime', how='outer')
        comm_factor_data.dropna(subset=list(comm_factor_data.columns)[2:], how='all', inplace=True)
        comm_factor_data.sort_values(by='datetime', inplace=True)
        comm_factor_data.reset_index(drop=True, inplace=True)
        comm_factor_data.to_csv(os.path.join(r'D:\commodity\data\hf_comm_factor_15t', '%s.csv' % commodity))
