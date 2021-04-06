import os
import pandas as pd
from utils.base_para import local_data_path
pd.set_option('expand_frame_repr', False)


file_list = []
dir_list = []
for roots, dirs, files in os.walk(local_data_path):
    if roots == local_data_path:

        if files:
            file_list = files
        if dirs:
            dir_list = dirs

for f in file_list:
    data_path = os.path.join(local_data_path, f)
    commodity = f[:-4].strip('1234567890')
    print(commodity)
    if commodity not in dir_list:
        os.mkdir(os.path.join(local_data_path, commodity))
        dir_list.append(commodity)
    os.rename(data_path, os.path.join(local_data_path, commodity, f))
