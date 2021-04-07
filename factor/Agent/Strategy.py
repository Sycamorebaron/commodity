import pandas as pd

pd.set_option('expand_frame_repr', False)


class AbsStrategy:
    def __init__(self):
        pass

    def cal_target_pos(self, *args):
        pass


class MAStrategy(AbsStrategy):
    def __init__(self, ma_para_list):
        AbsStrategy.__init__(self)
        self.para_list = ma_para_list

    def cal_target_pos(self, contract_dict, tm: str):
        rtn_pos = {}
        for contract_id in contract_dict.keys():

            contract = contract_dict[contract_id]
            data = contract.data_dict[contract.operate_contract]
            data = data.loc[data['trading_date'] <= pd.to_datetime(tm)]
            data = data[['datetime', 'close']]
            data = data.resample(on='datetime', rule='1D').agg(
                {
                    'close': 'last'
                }
            )
            data.dropna(inplace=True, axis=0)
            for ma_turn in self.para_list:
                data['ma_%s' % ma_turn] = data['close'].rolling(ma_turn).mean()
            last_trade_data = list(data.iloc[-1])
            long_order = 0

            for _ in range(0, len(self.para_list)):
                if last_trade_data[_] > last_trade_data[_ + 1]:
                    long_order += 1
                elif last_trade_data[_] < last_trade_data[_ + 1]:
                    long_order -= 1
                else:
                    pass
            rtn_pos[contract.operate_contract] = long_order / len(self.para_list) * 0.7
        return rtn_pos


if __name__ == '__main__':

    ma_strategy = MAStrategy(ma_para_list=[5, 10, 20, 60, 120])
