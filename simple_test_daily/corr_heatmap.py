import pandas as pd
from utils.base_para import NORMAL_CONTRACT_INFO
from genetic_algo.program.data_former import DataFormer
import seaborn as sns
from matplotlib import pyplot as plt

pd.set_option('expand_frame_repr', False)

for comm_info in NORMAL_CONTRACT_INFO:
    comm = comm_info['id']
    data_former = DataFormer(comm=comm)
    data = data_former.data
    corr = data[['high', '1dP1V0', '1dR2DV0', '1dkurt', '1ddown_rtn_std']].corr()
    sns.heatmap(corr, cmap='rainbow', annot=True, vmin=-1, vmax=1)
    plt.title(comm)
    plt.savefig(r'D:\commodity\data\1dheatmap\%s.png' % comm)
    plt.close()

