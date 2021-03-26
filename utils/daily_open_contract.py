import pandas as pd
from sqlalchemy import create_engine

pd.set_option('expand_frame_repr', False)

eg = create_engine("postgresql://postgres:thomas@localhost:5432/futures")

sql = 'select schemaname,tablename from pg_tables'
data = pd.read_sql_query(sql, con=eg)
print(data)
com_df_list = []
for i in range(len(data)):
    print(i, len(data))
    schemaname = data['schemaname'].iloc[i]
    tablename = data['tablename'].iloc[i]
    sql = 'select * from "%s"."%s"' % (schemaname, tablename)
    com_df = pd.read_sql_query(sql, con=eg)
    if schemaname in ['pg_catalog', 'information_schema']:
        continue
    try:
        com_df = com_df[[
            'datetime', 'order_book_id', 'trading_date', 'open', 'high', 'low', 'close', 'volume', 'open_interest',
            'total_turnover'
        ]].copy()
    except:
        print(schemaname, tablename)
        exit()


    com_df['datetime'] = pd.to_datetime(com_df['datetime'])
    com_df = com_df.resample(on='datetime', rule='1D').agg(
        {
            'order_book_id': 'last',
            'trading_date': 'last',
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'open_interest': 'last',
            'total_turnover': 'sum'
        }
    )
    com_df.dropna(subset=['open'], how='any', inplace=True)
    com_df.reset_index(inplace=True)
    com_df_list.append(com_df)

com_df_sum = pd.concat(com_df_list)
com_df_sum.reset_index(drop=True, inplace=True)

print(com_df_sum)
com_df_sum.to_sql('daily_open_contract', con=eg, schema='public', if_exists='replace')
