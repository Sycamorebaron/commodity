import pandas as pd

pd.set_option('expand_frame_repr', False)

contract_info = pd.read_csv(r'D:\futures_data\public\contract_info.csv')

contract_info = contract_info[[
    'order_book_id', 'underlying_symbol', 'margin_rate', 'maturity_date', 'listed_date', 'de_listed_date', 'contract_multiplier'
]]

info_list = []
for symbol in list(set(list(contract_info['underlying_symbol']))):
    open_contract = contract_info.loc[contract_info['underlying_symbol'] == symbol]

    open_contract = open_contract.loc[open_contract['listed_date'] != '0000-00-00']
    open_contract.sort_values(by='listed_date', inplace=True)
    open_contract.reset_index(drop=True, inplace=True)
    if symbol not in ['IF', 'IH', 'IC']:
        info_list.append(
            {
                'id': symbol,
                'month_list': list(
                    set([int(i) for i in list(open_contract['order_book_id'].apply(lambda x: x[-2:])) if int(i) < 13])
                ),
                'first_listed_date': open_contract['listed_date'].iloc[1],
                'last_de_listed_date': open_contract['de_listed_date'].iloc[-2],
                'init_margin_rate': open_contract['margin_rate'].max(),
                'contract_unit': open_contract['contract_multiplier'].iloc[-1],
                'open_comm': 5,
                'close_comm': 5
            }
        )
print(info_list)
