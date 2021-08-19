import pandas as pd
import os
import numpy as np
from genetic_algo.genetic_utils import continuous_contract_path, factor_path
pd.set_option('expand_frame_repr', False)


class DataFormer:
    def __init__(self, comm):
        self.comm = comm

    @property
    def data(self):
        return self.form_data()

    @property
    def drop_nainf_data(self):
        return self.form_drop_nainf_data()

    def form_drop_nainf_data(self):
        data = self.form_data()
        chosen = ['datetime']
        for col in data.columns[1:]:
            data.loc[np.isfinite(data[col]).apply(lambda x: not x), col] = np.nan

            if data[col].isna().sum() == 0:
                chosen.append(col)

        return data[chosen][:-1]

    def form_data(self):
        contract_data = pd.read_csv(os.path.join(continuous_contract_path, '%s.csv' % self.comm))[[
            'datetime', 'open', 'high', 'low', 'close', 'vol', 'oi'
        ]]
        factor_data = self._factor_data()
        m_data = contract_data.merge(factor_data, on='datetime', how='left')
        m_data['f_rtn'] = m_data['1dhf_rtn'].shift(-1)

        return m_data[:-1]

    def _factor_data(self):
        files = []
        for roots, dirs, files in os.walk(factor_path):
            if files:
                break
        merged_data = pd.DataFrame()

        for f in files:
            f_d = pd.read_csv(os.path.join(factor_path, f))[['datetime', self.comm]]
            f_d.columns = ['datetime', f.split('.')[0]]

            if len(merged_data):
                merged_data = merged_data.merge(f_d, on='datetime', how='outer')
            else:
                merged_data = f_d
        return merged_data


if __name__ == '__main__':

    data_former = DataFormer(comm='L')
    print(data_former.dropna_data)
