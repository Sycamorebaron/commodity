import pandas as pd
import os
from utils.base_para import NORMAL_CONTRACT_INFO
pd.set_option('expand_frame_repr', False)


dir_df = pd.DataFrame(NORMAL_CONTRACT_INFO)
print(dir_df)
dir_df.to_excel(r'C:\Users\sycam\Desktop\comm.xlsx')
print(dir_df)

