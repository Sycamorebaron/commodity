import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import seaborn as sns

factor_15t_path = r'C:\15t_factor'
comm_data_path = r'D:\commodity\data\hf_comm_factor_15t'
typical_comm = 'L'


def double_axis_pic(data, fst_col, sec_col):
    fig, ax = plt.subplots()
    ax.plot(data[fst_col], color='blue')
    ax2 = ax.twinx()
    ax2.plot(data[sec_col], color='red')
    plt.show()


def scatter_pic(data, fst_col, sec_col):
    plt.scatter(x=data[fst_col], y=data[sec_col])
    plt.show()


def rolling_corr(data, fst_col, sec_col, ts_len):
    data['%s_corr' % ts_len] = np.nan

    for i in range(ts_len, len(data)):
        t_data = data[i - ts_len: i]
        data['%s_corr' % ts_len].iloc[i] = t_data[fst_col].corr(t_data[sec_col])
    return data['%s_corr' % ts_len]


def seg_summary(data, factor, target, plt, segs=10):
    res = []
    for i in range(segs):
        if i == 0:
            seg_data = data.loc[data[factor] <= data[factor].quantile((i + 1) / segs)]
        else:
            seg_data = data.loc[
                (data[factor] > data[factor].quantile(i / segs)) &
                (data[factor] <= data[factor].quantile((i + 1) / segs))
            ]

        res.append(
            {
                'factor_mean': seg_data[factor].mean(),
                '%s_mean' % target: seg_data[target].mean()
            }
        )
    res_df = pd.DataFrame(res)
    print(res_df)
    plt.title('%s : %s' % (factor, target))
    plt.scatter(res_df['factor_mean'], res_df['%s_mean' % target])
    # plt.show()


def rolling_seg_summary(data, factor, target, segs=10, rolling_period=300):
    res = []

    for j in range(rolling_period, len(data), 1):  # 可以不要每个点都算，太费时
        print(j, len(data))
        t_data = data[j - rolling_period: j].copy()
        t_res = {'dt': data['datetime'].iloc[j - 1]}
        for i in range(segs):
            if i == 0:
                lower_bound = t_data[factor].min()
                upper_bound = t_data[factor].quantile((i + 1) / segs)
            else:
                lower_bound = t_data[factor].quantile(i / segs)
                upper_bound = t_data[factor].quantile((i + 1) / segs)

            if (data[factor].iloc[j] >= lower_bound) & (data[factor].iloc[j] < upper_bound):
                t_res['%sseg_target' % i] = data[target].iloc[j]
                break
        res.append(t_res)

    res_df = pd.DataFrame(res)
    res_df.fillna(0, inplace=True)

    for i in range(segs):
        if '%sseg_target' % i not in res_df.columns:
            continue
        res_df['%sseg_target' % i] = (1 + res_df['%sseg_target' % i]).cumprod()
    plt.plot(res_df[[('%sseg_target' % i) for i in range(segs)]])
    plt.legend([('%sseg_target' % i) for i in range(segs)])
    plt.show()


def corr_mat(data, factor_list):

    heatmap_data = data[factor_list].corr()
    print(heatmap_data)
    sns.heatmap(heatmap_data, annot=True, vmin=-1, vmax=1, cmap=plt.cm.get_cmap('seismic'))
    plt.show()


def sep_invalid_time(data):
    data['tm'] = data['datetime'].apply(lambda x: x.strftime('%H%M'))
    data = data.loc[data['tm'].apply(
        lambda x: x not in ['0900', '1015', '1330', '2100']
    )
    ]
    data.reset_index(drop=True, inplace=True)
    return data

def sep_extreme_value(data, factor):
    upper_bound = data[factor] <= data[factor].quantile(0.99)
    lower_bound = data[factor] >= data[factor].quantile(0.01)
    data = data.loc[upper_bound & lower_bound]
    data.reset_index(drop=True, inplace=True)
    return data
