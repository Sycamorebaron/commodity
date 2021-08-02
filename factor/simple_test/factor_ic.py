import pandas as pd
import os

pd.set_option('expand_frame_repr', False)

data_path = r'D:\commodity\data\output'
factor_path = r'C:\futures_factor'
factor = 'amihud'
rtn = 'f5_rtn'
commodity = 'FG'

factor_data = pd.read_excel(os.path.join(factor_path, '%s.xlsx' % factor))[['date', commodity]]
factor_data.columns = ['date', factor]
rtn_data = pd.read_excel(os.path.join(data_path, '%s.xlsx' % rtn))[['date', commodity]]
data = factor_data.merge(rtn_data, on='date', how='inner')
data.dropna(how='any', inplace=True, axis=0)
data.to_csv(r'cal_factor.csv')
print(data[[factor, commodity]])
print(data[[factor, commodity]].corr())


