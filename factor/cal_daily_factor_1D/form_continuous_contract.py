import pandas as pd
from utils.base_para import NORMAL_CONTRACT_INFO, local_1d_factor_path, OUTPUT_DATA_PATH
import os

pd.set_option('expand_frame_repr', False)

oi_oi = pd.read_csv(os.path.join(local_1d_factor_path, '1doi_oi.csv'))
vol_vol = pd.read_csv(os.path.join(local_1d_factor_path, '1dvol_vol.csv'))
c_o = pd.read_csv(os.path.join(local_1d_factor_path, '1dclose_open.csv'))
c_h = pd.read_csv(os.path.join(local_1d_factor_path, '1dclose_high.csv'))
c_l = pd.read_csv(os.path.join(local_1d_factor_path, '1dclose_low.csv'))
c_c = pd.read_csv(os.path.join(local_1d_factor_path, '1dclose_close.csv'))

for comm in c_c.columns[2:]:
    comm_o = c_o[['datetime', comm]].rename({comm:'open'}, axis=1)
    comm_h = c_h[['datetime', comm]].rename({comm:'high'}, axis=1)
    comm_l = c_l[['datetime', comm]].rename({comm:'low'}, axis=1)
    comm_c = c_c[['datetime', comm]].rename({comm:'close'}, axis=1)
    comm_vol = vol_vol[['datetime', comm]].rename({comm:'vol'}, axis=1)
    comm_oi = oi_oi[['datetime', comm]].rename({comm:'oi'}, axis=1)
    comm_data = comm_o.merge(comm_h, on='datetime', how='outer').merge(comm_l, on='datetime', how='outer')\
        .merge(comm_c, on='datetime', how='outer').merge(comm_vol, on='datetime', how='outer')\
        .merge(comm_oi, on='datetime', how='outer')

    comm_data['re_oi'] = (1 + comm_data['oi']).cumprod()
    comm_data['re_vol'] = (1 + comm_data['vol']).cumprod()
    comm_data['re_close'] = (1 + comm_data['close']).cumprod()


    comm_data['re_open'] = comm_data['re_close'].shift(1) * (1 + comm_data['open'])
    comm_data['re_high'] = comm_data['re_close'].shift(1) * (1 + comm_data['high'])
    comm_data['re_low'] = comm_data['re_close'].shift(1) * (1 + comm_data['low'])
    comm_data = comm_data[['datetime'] + [i for i in comm_data.columns if i.startswith('re_')]]
    comm_data.columns = ['datetime'] + [i.split('_')[1] for i in comm_data.columns if '_' in i]
    comm_data = comm_data[['datetime', 'open', 'high', 'low', 'close', 'vol', 'oi']][1:].reset_index(drop=True)
    comm_data = comm_data.dropna(subset=['open', 'high', 'low', 'close', 'vol', 'oi']).reset_index(drop=True)
    print(comm_data)

    comm_data.to_csv(r'D:\commodity\data\continuous_contract\%s.csv' % comm)