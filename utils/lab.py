import pandas as pd
import os

pd.set_option('expand_frame_repr', False)

# data_path = r'D:\commodity\data\hf_ic_15t'
#
# files = []
# for roots, dirs, files in os.walk(data_path):
#     if files:
#         break
#
# ic_df = pd.DataFrame()
# for f in files:
#     data = pd.read_csv(os.path.join(data_path, f))
#     data = data[['datetime', 'ic']]
#     data.columns = ['datetime', f.split('.')[0][3:-7]]
#
#     if len(ic_df):
#         ic_df = ic_df.merge(data, on='datetime', how='outer')
#     else:
#         ic_df = data
#
# ic_df = ic_df[ic_df.columns[1:]]
# corr_df = ic_df.corr(method='pearson')
# corr_df.to_excel(r'C:\Users\sycam\Desktop\corr.xlsx', sheet_name='pearson')
# # corr_df = ic_df.corr(method='spearman')
# # corr_df.to_excel(r'C:\Users\sycam\Desktop\corr.xlsx', sheet_name='spearman')


data = pd.read_excel(r'C:\Users\sycam\Desktop\工作簿1.xlsx')

hexin = []
jichu = []
for i in range(len(data)):

    if type(data['核心池'].iloc[i]) == str:
        hexin += data['核心池'].iloc[i].split('、')
    if type(data['基础池'].iloc[i]) == str:

        jichu += data['基础池'].iloc[i].split('、')

hexin_df = pd.DataFrame({'1': hexin})
jichu_df = pd.DataFrame({'1': jichu})
hexin_df.to_excel(r'C:\Users\sycam\Desktop\核心.xlsx')
jichu_df.to_excel(r'C:\Users\sycam\Desktop\基础.xlsx')
