import pandas as pd
from matplotlib import pyplot as plt

pd.set_option('expand_frame_repr', False)

rtn_path = r'C:\15t_factor\15Thf_rtn.csv'
data = pd.read_csv(rtn_path)
data['tm'] = data['datetime'].apply(lambda x: x.split(' ')[1])
for comm in data.columns[2:]:
    print(comm)
    c_data = data[[comm, 'tm']].copy()
    c_data.dropna(inplace=True)
    m_data = pd.DataFrame()
    legend = []
    for tm in list(c_data['tm'].drop_duplicates()):
        tm_data = c_data.loc[c_data['tm'] == tm].copy()
        tm_data.reset_index(drop=True, inplace=True)
        tm_data.columns = [tm, 'index']
        tm_data['index'] = tm_data.index

        legend.append('%s | %s | %s | %s' % (tm, round(tm_data[tm].quantile(0.975)-tm_data[tm].quantile(0.025), 6), round(tm_data[tm].quantile(0.975), 6), round(tm_data[tm].quantile(0.025), 6)))
        if len(m_data):
            m_data = m_data.merge(tm_data, on='index', how='outer')
        else:
            m_data = tm_data

    plt.figure(figsize=[10, 9])
    for tm in list(c_data['tm'].drop_duplicates()):
        plt.hist(m_data[tm], bins=30, stacked=True, alpha=0.5)
    plt.legend(legend)
    plt.title(comm)
    plt.savefig(r'C:\Users\sycam\Desktop\tm_data\%s.png' % comm)
    plt.close()





