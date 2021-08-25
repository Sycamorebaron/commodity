import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from genetic_algo.program.data_former import DataFormer
from utils.base_para import NORMAL_CONTRACT_INFO


class SimpleTest:
    def __init__(self, comm, hist_len):
        self.comm = comm
        self.hist_len = hist_len
        self.data_former = DataFormer(comm=comm)
        self.data = self.data_former.drop_nainf_data

    def add_factor(self, factor):

        # self.data['rank_1dkurt'] = self.data['1dkurt'].rolling(self.hist_len).apply(lambda x: len(x.loc[x < x.iloc[-1]]) / len(x))
        # self.data['sub_1'] = self.data['1droll_spread'] - self.data['rank_1dkurt']
        # self.data['factor'] = self.data['sub_1'] - self.data['rank_1dkurt']

        # self.data['factor'] = self.data['1ddown_rtn_mean']
        #
        # self.data['factor'] = self.data['1dopen_5t_pct'].apply(lambda x: np.sign(x) * x**4)
        self.data['factor'] = self.data[factor]

    def backtest(self):
        equity = pd.DataFrame()
        for factor in self.data.columns:
            print(self.comm, factor)
            if factor in ['f_rtn', 'datetime']:
                continue

            self.add_factor(factor)

            data = self.data[['datetime', 'factor', '1dhf_rtn']].copy()

            data['long_thresh'] = data['factor'].rolling(
                self.hist_len, min_periods=self.hist_len
            ).apply(lambda x: x.quantile(0.95))

            data['short_thresh'] = data['factor'].rolling(
                self.hist_len, min_periods=self.hist_len
            ).apply(lambda x: x.quantile(0.05))

            long_cond = data['factor'] > data['long_thresh']
            short_cond = data['factor'] < data['short_thresh']

            data['sig'] = 0
            data.loc[long_cond, 'sig'] = 1
            data.loc[short_cond, 'sig'] = -1

            data['pos'] = data['sig'].shift(1)
            data['rtn'] = data['1dhf_rtn'] * data['pos']
            data[factor] = (1 + data['rtn']).cumprod()

            if len(equity):
                equity = equity.merge(data[['datetime', factor]], on='datetime', how='outer')

            else:
                equity = data[['datetime', factor]]

        equity['datetime'] = pd.to_datetime(equity['datetime'].apply(lambda x: x.split(' ')[0]))
        equity.set_index('datetime', inplace=True)

        plt.plot(equity)
        plt.title(self.comm)

        plt.savefig(r'D:\commodity\data\daily_factor_eq\%s.png' % self.comm)
        equity.to_csv(r'D:\commodity\data\daily_factor_eq\%s.csv' % self.comm)
        plt.close()


if __name__ == '__main__':

    for comm_info in NORMAL_CONTRACT_INFO:
        comm = comm_info['id']
        simple_test = SimpleTest(
            comm=comm,
            hist_len=100
        )
        simple_test.backtest()