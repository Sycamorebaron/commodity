import pandas as pd
from utils.base_para import *
import os

data = pd.read_csv(os.path.join(INPUT_DATA_PATH, 'M_volume.csv'))
data = data[data.columns[1:]].copy()
data['datetime'] = pd.to_datetime(data['datetime'])

print(data)
data.to_sql('M_volume', con=eg, schema='M', if_exists='replace')