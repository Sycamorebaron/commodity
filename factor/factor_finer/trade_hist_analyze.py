import pandas as pd

pd.set_option('expand_frame_repr', False)

data = pd.read_csv(r'C:\Users\sycam\Desktop\fgreverse_trade_hist.csv')

trade_list = []
for i in range(0, len(data), 2):
    trade = data[i: i + 2].copy().reset_index(drop=True)

    trade_list.append(
        {
            'open_date': trade['now_date'].iloc[0],
            'contract': trade['contract'].iloc[0],
            'num': trade['num'].iloc[0],
            'side': trade['trade_type'].iloc[0].split('_')[0],
            'open_price': trade['price'].iloc[0],
            'close_price': trade['price'].iloc[1],
            'fee': trade['fee'].sum(),
            'profit': trade['price'].iloc[1] - trade['price'].iloc[0] if
            trade['trade_type'].iloc[0].split('_')[0] == 'long' else trade['price'].iloc[0] - trade['price'].iloc[1]
        }
    )

trade_info = pd.DataFrame(trade_list)
print(trade_info)
trade_info.to_csv(r'C:\Users\sycam\Desktop\fgreverse_trade_info.csv')