import pandas as pd
from paths import comm_data_path_30t, typical_comm, double_axis_pic, scatter_pic, \
    rolling_corr, seg_summary, rolling_seg_summary, corr_mat, sep_invalid_time, sep_extreme_value
import os
from matplotlib import pyplot as plt

pd.set_option('expand_frame_repr', False)

data = pd.read_csv(os.path.join(comm_data_path_30t, '%s.csv' % typical_comm))
data['datetime'] = pd.to_datetime(data['datetime'])

chosen_factor = 'rtn'

if chosen_factor not in ['rtn', 'highest_rtn', 'lowest_rtn']:
    data = data[['datetime', chosen_factor, 'rtn', 'highest_rtn', 'lowest_rtn']]
else:
    data = data[['datetime', 'rtn', 'highest_rtn', 'lowest_rtn']]
data = data.dropna(subset=[chosen_factor, 'highest_rtn', 'lowest_rtn'], how='all')
data['f_rtn'], data['f_c2h'], data['f_c2l'] = \
    data['rtn'].shift(-1), data['highest_rtn'].shift(-1), data['lowest_rtn'].shift(-1)
data['abs_f_rtn'] = data['f_rtn'].apply(lambda x: abs(x))
data['abs_rtn'] = data['rtn'].apply(lambda x: abs(x))

data = sep_invalid_time(data=data)
# data = sep_extreme_value(data, factor=chosen_factor)

# rolling_seg_summary(data=data, factor=chosen_factor, target='f_rtn', segs=10)

# ============== 极端值对比 =========================
plt.figure(figsize=[15, 10])
plt.subplot(231)
seg_summary(data=data, factor=chosen_factor, target='f_rtn', plt=plt, segs=30)
plt.subplot(232)
seg_summary(data=data, factor=chosen_factor, target='f_c2h', plt=plt, segs=30)
plt.subplot(233)
seg_summary(data=data, factor=chosen_factor, target='f_c2l', plt=plt, segs=30)


data = sep_extreme_value(data, factor=chosen_factor)
plt.subplot(234)
seg_summary(data=data, factor=chosen_factor, target='f_rtn', plt=plt, segs=30)
plt.subplot(235)
seg_summary(data=data, factor=chosen_factor, target='f_c2h', plt=plt, segs=30)
plt.subplot(236)
seg_summary(data=data, factor=chosen_factor, target='f_c2l', plt=plt, segs=30)
plt.show()
# ==================================================

# factor_list = [
#     '15Tabig_rtn_mean', '15Tdoi_rtn_corr', '15Tdown_move_vol_pct', '15Thf_rtn', '15Tmean', '15Ttrend_ratio',
#     '15Tvbig_rtn_mean'
# ]
# corr_mat(data=data, factor_list=factor_list)



# double_axis_pic(data, chosen_factor, 'f_rtn')
# scatter_pic(data, chosen_factor, 'f_c2l')

# data['100_corr'] = rolling_corr(data=data.copy(), fst_col=chosen_factor, sec_col='f_rtn', ts_len=100)

# data['exp_ic'] = data['100_corr'].expanding().sum()
# plt.plot(data['exp_ic'])
# plt.show()
