import pandas as pd
from statsmodels.tsa.stattools import adfuller

pd.set_option('expand_frame_repr', False)


class PreProcess:
    def stationalize(self, data, targets):
        for col in targets:
            adf_res = adfuller(x=data[col])
            if adf_res[1] > 0.05:
                data['d_%s' % col] = data[col] - data[col].shift(1)
                data.drop(col, inplace=True, axis=1)
        data = data[1:].reset_index(drop=True)
        return data
