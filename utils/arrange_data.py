import os
import pandas as pd

pd.set_option('expand_frame_repr', False)

file_list = []
dir_list = []
for roots, dirs, files in os.walk(r'D:\futures_data'):
    if roots == r'D:\futures_data':

        if files:
            file_list = files
        if dirs:
            dir_list = dirs

for f in file_list:
    data_path = os.path.join(r'D:\futures_data', f)
    commodity = f[:-4].strip('1234567890')
    print(commodity)
    if commodity not in dir_list:
        os.mkdir(r'D:\futures_data\%s' % commodity)
        dir_list.append(commodity)
    os.rename(data_path, os.path.join(r'D:\futures_data', commodity, f))

