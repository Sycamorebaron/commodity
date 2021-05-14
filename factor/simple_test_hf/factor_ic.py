import pandas as pd
import os
from matplotlib import pyplot as plt
pd.set_option('expand_frame_repr', False)

data_path = r'D:\commodity\data\hf_comm_factor'


for roots, dirs, files in os.walk(data_path):
    if files:
        factor_corr = {}
        for f in files:
            d = pd.read_csv(os.path.join(data_path, f))
            d['datetime'] = pd.to_datetime(d['datetime'])
            d = d[d.columns[1:]]
            d['f_rtn'] = d['rtn'].shift(-1)
            d = d[1:].copy()
            open_cond = (d['datetime'].dt.hour == 9) & (d['datetime'].dt.minute == 0)

            for col in d.columns[1:-2]:
                factor_corr[col] = d['f_rtn'].corr(d[col])
            factor_corr_df = pd.DataFrame(factor_corr, index=['corr']).T
            print(factor_corr_df)
            plt.bar(list(factor_corr_df.index), height=factor_corr_df['corr'])

            d = d.loc[open_cond.apply(lambda x: not x)].copy()

            d.reset_index(drop=True, inplace=True)

            for col in d.columns[1:-2]:
                factor_corr[col] = d['f_rtn'].corr(d[col])
            factor_corr_df = pd.DataFrame(factor_corr, index=['corr']).T
            print(factor_corr_df)
            plt.bar(['noopen' + i for i in list(factor_corr_df.index)], height=factor_corr_df['corr'], color='red')

            plt.title(f)
            plt.show()

