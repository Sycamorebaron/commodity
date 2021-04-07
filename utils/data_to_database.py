import os
import pandas as pd
import multiprocessing
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateSchema
pd.set_option('expand_frame_repr', False)


def to_database(data_set, proc_id):

    local_data_path = r'D:\futures_data'
    engine = create_engine("postgresql://postgres:thomas@localhost:5432/futures")
    i = 0
    for f in data_set:
        print('PROC', proc_id, '||', i, '/' ,len(data_set), f)
        data = pd.read_csv(os.path.join(local_data_path, f))
        if not len(data):
            print(f, 'PASS')
            continue
        if f.startswith('contract_info'):
            data.to_sql('contract_info', con=engine, schema='public', if_exists='replace')
            continue

        symbol = f[:-4].strip('1234567890')

        # 如果schema不存在则创建
        # if not engine.dialect.has_schema(engine, symbol):
        #     engine.execute(CreateSchema(symbol))
        #     print(symbol)
        # else:
        #     print(f)

        data = data[[
            'order_book_id', 'datetime', 'trading_date', 'open', 'high', 'low', 'close', 'volume',
            'open_interest', 'total_turnover'
        ]]
        data.to_sql(f[:-4], con=engine, schema=symbol, if_exists='replace')
        # print(f, 'TO SQL')
        i += 1

def show(s):
    print('启动！')
    print(s)

if __name__ == '__main__':

    d_local_data_path = r'D:\futures_data'

    local_data = []

    for roots, dirs, files in os.walk(d_local_data_path):
        if files:
            local_data = files
    local_data = [i for i in local_data if i != 'contract_info.csv']

    pool = multiprocessing.Pool(processes=8)

    n_set = 4
    start = 0
    for set in range(n_set):

        if set == (n_set - 1):
            t_data_set = local_data[start:]
        else:
            t_data_set = local_data[start: int(len(local_data) / n_set * (set + 1))]

        start += int(len(local_data) / n_set)

        pool.apply_async(to_database, (t_data_set, set, ))
        # pool.apply_async(show, (t_data_set,))

    pool.close()
    pool.join()
