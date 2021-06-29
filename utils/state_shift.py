import pandas as pd
import json

from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
pd.set_option('expand_frame_repr', False)
xmajorLocator  = MultipleLocator(182)
with open(r'D:\commodity\factor\backtest\state_shift_mat.json') as f:
    d = json.load(f)

comm_list = []
for i in range(len(d)):
    comm_list += list(d[i].keys())
comm_list = list(set(comm_list))
comm_list.remove('date')

for comm in comm_list:
    print(comm)
    res = []
    for i in range(len(d)):
        if comm not in d[i]:
            continue
        t_mat = d[i][comm]

        res.append(
            {
                'date': d[i]['date'],
                'neg_neg': t_mat[0][0] / sum(t_mat[0]) if sum(t_mat[0]) != 0 else 0,
                # 'neg_neu': t_mat[0][1] / sum(t_mat[0]) if sum(t_mat[0]) != 0 else 0,
                'neg_pos': t_mat[0][2] / sum(t_mat[0]) if sum(t_mat[0]) != 0 else 0,
                # 'neu_neg': t_mat[1][0] / sum(t_mat[1]) if sum(t_mat[1]) != 0 else 0,
                # 'neu_pos': t_mat[1][2] / sum(t_mat[1]) if sum(t_mat[1]) != 0 else 0,
                'pos_neg': t_mat[2][0] / sum(t_mat[2]) if sum(t_mat[2]) != 0 else 0,
                # 'pos_neu': t_mat[2][1] / sum(t_mat[2]) if sum(t_mat[2]) != 0 else 0,
                'pos_pos': t_mat[2][2] / sum(t_mat[2]) if sum(t_mat[2]) != 0 else 0,
            }
        )

    res_df = pd.DataFrame(res)
    res_df.set_index('date', inplace=True)
    ax = plt.subplot(111)
    ax.plot(res_df)
    ax.xaxis.set_major_locator(xmajorLocator)
    ax.legend(res_df.columns, loc='right')
    plt.title(comm)

    plt.savefig(r'D:\commodity\data\state_shift_mat\%s.png' % comm)
    plt.close()


