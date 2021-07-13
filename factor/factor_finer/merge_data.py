import pandas as pd
import os
from paths import factor_15t_path, comm_data_path

pd.set_option('expand_frame_repr', False)

def comm_data(data_dict, comm):
    print(comm)
    d = pd.DataFrame()
    for f in data_dict.keys():
        data = data_dict[f]

        data['datetime'] = pd.to_datetime(data['datetime'])
        data = data[['datetime', comm]]
        data.columns = ['datetime', f.split('.')[0]]

        if len(d):
            d = d.merge(data, on='datetime', how='outer')
        else:
            d = data
    d = d.sort_values(by='datetime', ascending=True)
    d.reset_index(drop=True, inplace=True)
    d = d.dropna(subset=[i for i in d.columns if i != 'datetime'], how='all')
    d.set_index('datetime', inplace=True)
    d.to_csv(os.path.join(comm_data_path, '%s.csv' % comm))


if __name__ == '__main__':
    files = []
    for roots, dirs, files in os.walk(factor_15t_path):
        if files:
            break
    data_dict = {}
    for f in files:
        data = pd.read_csv(os.path.join(factor_15t_path, f))
        data_dict[f] = data

    for comm in [
        'L', 'C', 'M', 'RU', 'SR', 'A', 'AL', 'P', 'ZN', 'V', 'CF', 'RO', 'RB', 'ER', 'CU', 'AU', 'Y', 'TA', 'PB', 'J',
        'ME', 'AG', 'OI', 'FG', 'RM', 'JM', 'TC', 'BU', 'I', 'JD', 'FB', 'PP', 'HC', 'MA', 'SF', 'SM', 'CS', 'SN', 'NI',
        'ZC', 'CY', 'AP', 'SC', 'SP', 'EG', 'CJ', 'UR', 'NR', 'SS', 'EB', 'SA', 'PG', 'LU', 'PF', 'BC', 'LH', 'PK'
    ]:
        data = comm_data(
            data_dict=data_dict,
            comm=comm
        )

