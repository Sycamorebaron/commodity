import pandas as pd
from utils.base_para import OUTPUT_DATA_PATH
import os
pd.set_option('expand_frame_repr', False)


daily_rtn_data = pd.read_excel(os.path.join(OUTPUT_DATA_PATH, 'daily_rtn.xlsx'))
print(daily_rtn_data)
comm_list = list(set([i.split('_')[0] for i in daily_rtn_data.columns[2:]]))
comm_list.sort()
print(comm_list)


for l_term in [1, 2, 3, 4, 5]:
    last_rtn_df = pd.DataFrame(daily_rtn_data['date'])
    for comm in comm_list:
        last_rtn_df[comm] = daily_rtn_data['%s_main_day_rtn' % comm].shift(l_term)
    last_rtn_df.to_excel(os.path.join(OUTPUT_DATA_PATH, 'l%sday_rtn.xlsx' % l_term))
    print(last_rtn_df)

