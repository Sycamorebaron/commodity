import pandas as pd
from utils.base_para import *
import os

data = pd.read_excel(os.path.join(INPUT_DATA_PATH, 'szzs.xlsx'))

data = data[['日期', '收盘价(元)']]
data.columns = ['date', 'close']

data.to_sql('szzs', con=eg, schema='public', if_exists='replace')




