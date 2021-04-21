import pandas as pd
import os
from statsmodels.tsa.stattools import adfuller
import sklearn.tree as st
from sklearn.decomposition import PCA
from matplotlib import pyplot as plt

pd.set_option('expand_frame_repr', False)

data_path = 'D:\commodity\data\output'
raw_data = pd.read_excel(os.path.join(data_path, 'fg_test_data.xlsx'))

for col in raw_data[2: -1]:
    plt.scatter(raw_data[1:])
