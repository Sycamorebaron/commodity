import pandas as pd
import os

pd.set_option('expand_frame_repr', False)

data_path = r'/data/daily_factor_eq'

files = []
for roots, dirs, files in os.walk(data_path):
    if files:
        break

comm_data = {}
for f in files:
    if f.endswith('csv'):
        comm_data[f.split('.')[0]] = pd.read_csv(os.path.join(data_path, f))

rtn_max_dd = {}
rtn_res = {}
for factor in comm_data[list(comm_data.keys())[0]].columns:
    if factor in ['datetime']:
        continue
    rtn_max_dd[factor] = {}
    rtn_res[factor] = {}
    for comm in comm_data.keys():
        if factor not in comm_data[comm].columns:
            continue
        rtn = comm_data[comm][factor].iloc[-1] - 1
        if rtn > 0:
            pass
        else:
            comm_data[comm][factor] = - comm_data[comm][factor]

        max_dd = (comm_data[comm][factor].expanding().max() - comm_data[comm][factor]).max()
        rtn_max_dd[factor][comm] = rtn / max_dd
        rtn_res[factor][comm] = rtn

pd.DataFrame(rtn_max_dd).to_csv(r'rtn_max_dd.csv')
pd.DataFrame(rtn_res).to_csv(r'rtn.csv')
