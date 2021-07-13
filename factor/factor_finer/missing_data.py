import pandas as pd
from paths import comm_data_path, typical_comm
import os

pd.set_option('expand_frame_repr', False)

data = pd.read_csv(os.path.join(comm_data_path, '%s.csv' % typical_comm))
data = data.dropna(subset=[i for i in data.columns if i not in ['15Thf_rtn', 'datetime']], how='all')


res = []
for col in data.columns[1:]:
    res.append({'factor': col, 'pct': '%s / %s' % (data[col].isnull().sum(), len(data))})
print(pd.DataFrame(res))




