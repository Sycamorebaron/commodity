import xgboost as xgb
import pandas as pd
from matplotlib import pyplot as plt
pd.set_option('expand_frame_repr', False)

data = pd.read_csv(r'/home/sycamore/2012_signal_df.csv')
data = data[['PB', 'L', 'C', 'M', 'SR', 'A', 'AL', 'P', 'ZN', 'RU']][:230].copy()
data['P'] *= 100
train_data = data[:200].reset_index(drop=True)
test_data = data[229:][['PB', 'L', 'C', 'M', 'SR', 'A', 'AL', 'P', 'ZN']].reset_index(drop=True)

model = xgb.XGBRegressor(n_estimators=7, objective='reg:squarederror')
model.fit(X=train_data[['PB', 'L', 'C', 'M', 'SR', 'A', 'AL', 'RU', 'ZN']], y=train_data['P'])

pred_res = model.predict(X=test_data)
print(pred_res)
exit()
real_res = pd.DataFrame(data[200:]['P'].reset_index(drop=True))
real_res['pred'] = pd.DataFrame(pred_res)[0]
plt.scatter(x=real_res['pred'], y=real_res['P'])
plt.show()

print(real_res)

"""
预测指标可以变
涨跌超过千一的dummy，带正负

"""

