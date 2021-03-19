import pandas as pd
import rqdatac as rq
import os

pd.set_option('expand_frame_repr', False)


class RQDataRenew:
    def __init__(self, lic, local_data_path):
        rq.init('license',
                lic,
                ("rqdatad-pro.ricequant.com", 16011)
                )
        self.contract_info = rq.all_instruments(type='Future')
        self.local_data_path = local_data_path
        self.contract_info.to_csv(os.path.join(local_data_path, 'contract_info.csv'), encoding='utf-8-sig')
        print(self.contract_info)

    def _renew_old_data(self):
        local_contract = []
        for roots, dirs, files in os.walk(self.local_data_path):
            if files:
                local_contract = files

        for f in local_contract:
            if f[:-4] in list(self.contract_info['order_book_id']):
                data = pd.read_csv(os.path.join(self.local_data_path, f))
                if len(data) != 0:
                    data.sort_values(by='trading_date', inplace=True)
                    local_last_date = data['trading_date'].iloc[-1]
                    maturity_date = self.contract_info.loc[
                        self.contract_info['order_book_id'] == f[:-4], 'maturity_date'].values[0]

                    if local_last_date != maturity_date:


                    print(local_last_date)
                    print(maturity_date)
                    exit()

        pass

    def _fetch_new_data(self):
        pass

    def renew_data(self):

        self._renew_old_data()
        self._fetch_new_data()


if __name__ == '__main__':
    d_license = \
        'SxqYJbyhuet-TZTiuD-8mWq4p8a8_fWCm_kKIGOtvI-YroINZrYk3EpjXfDzgHgb3ZvgPnWHPBREchrSCmxo4F0JcuSRNoJYJtQSWIzdJKK'\
        'c-7RpG39W8LVVGQfCoV3xoT1AbhJhQEh53JjIrq8ly6AFOnRhmTiEFQ01jsaG2Vc=dCeQGaTQbKjRLpXzg9Id09e8LUe_E3SZO99MriEW86'\
        'JCicssARrtWqOWp4Ncd0nDA9j4i8rIuf8sUGWQYenJe5siyHgxm9y2SUZugSu26aJJe1-hqCzHUB8TLHgM_Db92EAF0npNAFzCSitgmqztK'\
        'G4JDG2GjtYPs5_tTKlqqPI='
    d_local_data_path = r'E:\futures_data'

    rq_data_renew = RQDataRenew(
        lic=d_license,
        local_data_path=d_local_data_path
    )

    rq_data_renew.renew_data()
