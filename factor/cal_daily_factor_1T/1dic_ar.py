import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('expand_frame_repr', False)
data = pd.read_csv(r'D:\commodity\data\1d_exp_ic.csv')

hist_t = 1
f_t = 1
res = {}
for col in data.columns[2:]:
    data['%s_hist' % col] = data[col] - data[col].shift(hist_t)
    data['%s_f' % col] = data[col].shift(-f_t) - data[col]
    res[col] = data['%s_hist' % col].corr(data['%s_f' % col])
    # print(col, data['%s_hist' % col].corr(data['%s_f' % col]))
res_df = pd.DataFrame(res, index=['corr']).T

plt.bar(x=res_df.index, height=res_df['corr'])
plt.title('%s || %s' % (hist_t, f_t))
plt.show()
