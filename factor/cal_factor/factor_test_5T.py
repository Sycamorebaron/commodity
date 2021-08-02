from utils.base_para import *
import pandas as pd
from sklearn.decomposition import PCA
import numpy as np
from dateutil.relativedelta import relativedelta
import statsmodels.api as sm
from factor.cal_factor.factor_test import FactorTest

pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', 200)


class HF5TFactor(FactorTest):
    # 休息时间：10:15-10:30
    def resample(self, data, rule):
        data = data.resample(on='datetime', rule=rule).agg(
            {
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
                'open_interest': 'last',
                'total_turnover': 'sum'
            }
        )
        data.dropna(subset=['open'], inplace=True)
        data.reset_index(inplace=True)
        data = data.loc[
            data['datetime'].apply(lambda x: (x.strftime('%H:%M') != '11:30') & (x.strftime('%H:%M') != '15:00'))]

        return data

    @staticmethod
    def add_label(data):
        data['label'] = data['datetime'].apply(
            # lambda x: x - relativedelta(minutes=1) if (x.strftime('%M') in ['01', '16', '31', '46']) else None
            lambda x: x - relativedelta(minutes=1) if (
                x.strftime('%M') in ['01', '06', '11', '16', '21', '26', '31', '36', '41', '46', '51', '56']
            ) else None
            )
        data['label'].fillna(method='ffill', inplace=True)
        return data


class HF5TBatch1(HF5TFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        HF5TFactor.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.mean_5t = []
        self.lowest_rtn_5t = []
        self.highest_rtn_5t = []
        self.amihud = []
        self.doi_pct = []

    def _daily_process(self):
        print(self.agent.earth_calender.now_date)

        open_comm_list = []

        for comm in self.exchange.contract_dict.keys():
            # 未上市的商品
            if self.exchange.contract_dict[comm].first_listed_date > self.agent.earth_calender.now_date:
                continue
            # 已经退市的商品
            if self.exchange.contract_dict[comm].last_de_listed_date < self.agent.earth_calender.now_date:
                continue
            print(comm)

            self.exchange.contract_dict[comm].renew_main_sec_contract(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[comm].renew_operate_contract(now_date=self.agent.earth_calender.now_date)
            open_comm_list.append(comm)

        t_factor_dict = self.t_daily_factor(open_comm_list)

        self.mean_5t.append(t_factor_dict['mean_5t'])
        self.lowest_rtn_5t.append(t_factor_dict['lowest_rtn_5t'])
        self.highest_rtn_5t.append(t_factor_dict['highest_rtn_5t'])
        self.amihud.append(t_factor_dict['amihud'])
        self.doi_pct.append(t_factor_dict['doi_pct'])

    def t_daily_factor(self, open_comm_list):

        _factor_dict = {
            'mean_5t': pd.DataFrame(),
            'lowest_rtn_5t': pd.DataFrame(),
            'highest_rtn_5t': pd.DataFrame(),
            'amihud': pd.DataFrame(),
            'doi_pct': pd.DataFrame(),
        }
        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            if len(today_data):

                today_data = self.add_label(data=today_data)
                today_data['rtn'] = today_data['close'] / today_data['open'] - 1

                res = pd.DataFrame(today_data.groupby('label').apply(self._cal))
                res['mean_5t'] = res[0].apply(lambda x: x['mean_5t'])
                res['lowest_rtn_5t'] = res[0].apply(lambda x: x['lowest_rtn_5t'])
                res['highest_rtn_5t'] = res[0].apply(lambda x: x['highest_rtn_5t'])
                res['amihud'] = res[0].apply(lambda x: x['amihud'])
                res['doi_pct'] = res[0].apply(lambda x: x['doi_pct'])

                res['datetime'] = res.index

                for factor in _factor_dict.keys():

                    if len(_factor_dict[factor]):
                        _factor_dict[factor] = _factor_dict[factor].merge(
                            res[['datetime', factor]].rename({factor: comm}, axis=1).reset_index(drop=True)
                        )
                    else:
                        _factor_dict[factor] = \
                            res[['datetime', factor]].rename({factor: comm}, axis=1).reset_index(drop=True)
        return _factor_dict

    def _cal(self, x):
        return {
            'mean_5t': x['rtn'].mean(),
            'lowest_rtn_5t': x['low'].min() / x['open'].iloc[0] - 1,
            'highest_rtn_5t': x['high'].max() / x['open'].iloc[0] - 1,
            'amihud': x['rtn'].mean() / x['volume'].sum() if x['volume'].sum() > 0 else 0,
            'doi_pct': x['open_interest'].iloc[-1] / x['open_interest'].iloc[0] - 1
        }


if __name__ == '__main__':
    cal_factor = HF5TBatch1(
        factor_name='moment',
        begin_date='2011-01-01',
        end_date='2021-02-28',
        init_cash=1000000,
        # contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] in ['L', 'M', 'C']],
        contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    mean_5t = pd.concat(cal_factor.mean_5t)
    lowest_rtn_5t = pd.concat(cal_factor.lowest_rtn_5t)
    highest_rtn_5t = pd.concat(cal_factor.highest_rtn_5t)
    amihud = pd.concat(cal_factor.amihud)
    doi_pct = pd.concat(cal_factor.doi_pct)

    mean_5t.reset_index(drop=True, inplace=True)
    lowest_rtn_5t.reset_index(drop=True, inplace=True)
    highest_rtn_5t.reset_index(drop=True, inplace=True)
    amihud.reset_index(drop=True, inplace=True)
    doi_pct.reset_index(drop=True, inplace=True)

    mean_5t.to_csv(os.path.join(OUTPUT_DATA_PATH, '5THFfactor', '5Tmean.csv'))
    lowest_rtn_5t.to_csv(os.path.join(OUTPUT_DATA_PATH, '5THFfactor', '5Tlowest_rtn.csv'))
    highest_rtn_5t.to_csv(os.path.join(OUTPUT_DATA_PATH, '5THFfactor', '5Thighest_rtn.csv'))
    amihud.to_csv(os.path.join(OUTPUT_DATA_PATH, '5THFfactor', '5Tamihud.csv'))
    doi_pct.to_csv(os.path.join(OUTPUT_DATA_PATH, '5THFfactor', '5Tdoi_pct.csv'))
