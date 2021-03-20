import pandas as pd
import rqdatac as rq
import os
from datetime import timedelta
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateSchema



pd.set_option('expand_frame_repr', False)


class RQDataRenew:
    def __init__(self, lic, local_data_path, engine):
        rq.init('license',
                lic,
                ("rqdatad-pro.ricequant.com", 16011)
                )
        self.contract_info = rq.all_instruments(type='Future')
        self.local_data_path = local_data_path
        self.contract_info.to_csv(os.path.join(local_data_path, 'contract_info.csv'), encoding='utf-8-sig')
        self.engine = engine
        print(self.contract_info)

    def _renew_old_data(self):
        local_contract = []
        for roots, dirs, files in os.walk(self.local_data_path):
            if files:
                local_contract = files

        for f in local_contract:
            if f[:-4] in list(self.contract_info['order_book_id']):
                local_data = pd.read_csv(os.path.join(self.local_data_path, f))
                if len(local_data) != 0:
                    local_data.sort_values(by='trading_date', inplace=True)
                    local_last_date = local_data['trading_date'].iloc[-1]
                    maturity_date = self.contract_info.loc[
                        self.contract_info['order_book_id'] == f[:-4], 'maturity_date'].values[0]

                    if local_last_date != maturity_date:
                        start_time = (pd.to_datetime(local_last_date) - timedelta(days=5)).strftime('%Y-%m-%d')
                        end_time = maturity_date

                        data = rq.get_price(
                            order_book_ids=f[:-4],
                            start_date=start_time,
                            end_date=end_time,
                            frequency='1m',
                            fields=['open', 'high', 'low', 'close', 'volume', 'open_interest', 'total_turnover'],
                            expect_df=True
                        )

                        data.reset_index(inplace=True)

                        data['trading_date'] = data['datetime'].apply(lambda x: x.strftime('%Y-%m-%d'))

                        sum_data = pd.concat([local_data, data])
                        sum_data.drop_duplicates(inplace=True)
                        sum_data.to_csv(os.path.join(self.local_data_path, f))
                        print(f[:-4], 'RENEW')
                    else:
                        print(f[:-4], 'FULL')

    def _fetch_new_data(self):
        local_files = []
        for roots, dirs, files in os.walk(self.local_data_path):
            if files:
                local_files = files

        new_open_contract = []
        for contract in list(self.contract_info['order_book_id']):
            if '连续' in self.contract_info.loc[self.contract_info['order_book_id'] == contract, 'symbol'].values[0]:
                print(
                    self.contract_info.loc[self.contract_info['order_book_id'] == contract, 'symbol'].values[0], 'PASS'
                )
                continue
            if '%s.csv' % contract not in local_files:
                new_open_contract.append(contract)

        for contract in new_open_contract:
            start_time = self.contract_info.loc[
                self.contract_info['order_book_id'] == contract, 'listed_date'
            ].values[0]
            end_time = self.contract_info.loc[
                self.contract_info['order_book_id'] == contract, 'de_listed_date'
            ].values[0]
            data = rq.get_price(
                order_book_ids=contract,
                start_date=pd.to_datetime(start_time),
                end_date=pd.to_datetime(end_time),
                frequency='1m',
                fields=['open', 'high', 'low', 'close', 'volume', 'open_interest', 'total_turnover'],
                expect_df=True
            )
            print(data)
            exit()
            if type(data) == type(pd.DataFrame()):
                data = data[['open', 'high', 'low', 'close', 'volume', 'open_interest',
                             'total_turnover']]
                data.to_csv(os.path.join(self.local_data_path, '%s.csv' % contract))
            else:
                pd.DataFrame().to_csv(os.path.join(self.local_data_path, '%s.csv' % contract))

    def _sort_data(self):
        local_data = []
        for roots, dirs, files in os.walk(self.local_data_path):
            if files:
                local_data = files

        for f in local_data:
            data = pd.read_csv(os.path.join(self.local_data_path, f))
            if not len(data):
                print(f, 'PASS')
                continue
            if f.startswith('contract_info'):
                continue

            data.sort_values(by='datetime', inplace=True)
            data.reset_index(drop=True, inplace=True)
            data.to_csv(os.path.join(self.local_data_path, f))
            print(f, 'SORT')

    def renew_data(self):

        self._renew_old_data()
        self._fetch_new_data()
        self._sort_data()

if __name__ == '__main__':
    d_license = \
        'SxqYJbyhuet-TZTiuD-8mWq4p8a8_fWCm_kKIGOtvI-YroINZrYk3EpjXfDzgHgb3ZvgPnWHPBREchrSCmxo4F0JcuSRNoJYJtQSWIzdJKK'\
        'c-7RpG39W8LVVGQfCoV3xoT1AbhJhQEh53JjIrq8ly6AFOnRhmTiEFQ01jsaG2Vc=dCeQGaTQbKjRLpXzg9Id09e8LUe_E3SZO99MriEW86'\
        'JCicssARrtWqOWp4Ncd0nDA9j4i8rIuf8sUGWQYenJe5siyHgxm9y2SUZugSu26aJJe1-hqCzHUB8TLHgM_Db92EAF0npNAFzCSitgmqztK'\
        'G4JDG2GjtYPs5_tTKlqqPI='
    d_local_data_path = r'E:\futures_data'
    d_engine = create_engine("postgresql://postgres:thomas@localhost:5432/futures")

    rq_data_renew = RQDataRenew(
        lic=d_license,
        local_data_path=d_local_data_path,
        engine=d_engine
    )

    rq_data_renew.renew_data()
