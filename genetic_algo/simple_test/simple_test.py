import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from genetic_algo.program.data_former import DataFormer



class SimpleTest:
    def __init__(self, comm, hist_len):
        self.comm = comm
        self.hist_len = hist_len
        self.data_former = DataFormer(comm=comm)
        self.data = self.data_former.drop_nainf_data

    def add_factor(self):

        self.data['scale'] = abs(self.data['1dvbig_rtn_vol']).rolling(self.hist_len, min_periods=self.hist_len).sum()
        # self.data['factor'] = (self.data['1dvbig_rtn_vol'] / self.data['scale']).apply(lambda x: np.cos(x))

        self.data['factor'] = - self.data['1dd_first_com'] / self.data['1dstd']

    def backtest(self):
        self.add_factor()
        data = self.data[['datetime', 'factor', '1dhf_rtn']]

        data['long_thresh'] = data['factor'].rolling(
            self.hist_len, min_periods=self.hist_len
        ).apply(lambda x: x.quantile(0.9))

        data['short_thresh'] = data['factor'].rolling(
            self.hist_len, min_periods=self.hist_len
        ).apply(lambda x: x.quantile(0.1))

        long_cond = data['factor'] > data['long_thresh']
        short_cond = data['factor'] < data['short_thresh']

        data['sig'] = 0
        data.loc[long_cond, 'sig'] = 1
        data.loc[short_cond, 'sig'] = -1

        data['pos'] = data['sig'].shift(1)
        data['rtn'] = data['1dhf_rtn'] * data['pos']
        data['equity'] = (1 + data['rtn']).cumprod()
        data['datetime'] = pd.to_datetime(data['datetime'].apply(lambda x: x.split(' ')[0]))
        data.set_index('datetime', inplace=True)

        plt.plot(data['equity'])
        plt.show()


if __name__ == '__main__':
    comm = 'PB'
    simple_test = SimpleTest(
        comm=comm,
        hist_len=300
    )
    simple_test.backtest()