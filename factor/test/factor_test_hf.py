from utils.base_para import *
import pandas as pd
from sklearn.decomposition import PCA
import numpy as np
from dateutil.relativedelta import relativedelta
import statsmodels.api as sm
from factor.test.factor_test import FactorTest

pd.set_option('expand_frame_repr', False)
pd.set_option('display.max_rows', 200)


class HFFactor(FactorTest):
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
        data = data.loc[data['datetime'].apply(lambda x: (x.strftime('%H:%M') != '11:30') & (x.strftime('%H:%M') != '15:00'))]

        return data


class HFRtn(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.rtn_30t = []

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

        daily_rtn_30t = self.t_daily_factor(open_comm_list)

        self.rtn_30t.append(daily_rtn_30t)

    def t_daily_factor(self, open_comm_list):

        _rtn_df = pd.DataFrame()
        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            if len(today_data):
                data_30t = self.resample(today_data.copy(), rule='30T')
                data_30t['rtn'] = (data_30t['close'] / data_30t['open']) - 1
                data_30t = data_30t[['datetime', 'rtn']]
                data_30t.columns = ['datetime', comm]
                if len(_rtn_df):
                    _rtn_df = _rtn_df.merge(data_30t, on='datetime', how='outer')
                else:
                    _rtn_df = data_30t

        return _rtn_df


class HFRtnMoment(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.factor_name = factor_name
        self.mean = []
        self.std = []
        self.skew = []
        self.kurt = []

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

        self.mean.append(t_factor_dict['mean'])
        self.std.append(t_factor_dict['std'])
        self.skew.append(t_factor_dict['skew'])
        self.kurt.append(t_factor_dict['kurt'])

    def _cal(self, x):
        return {
            'mean': x['rtn'].mean(),
            'std': x['rtn'].std(ddof=1),
            'skew': x['rtn'].skew(),
            'kurt': x['rtn'].kurtosis()
        }

    def t_daily_factor(self, open_comm_list):

        _factor_dict = {
            'mean': pd.DataFrame(),
            'std': pd.DataFrame(),
            'skew': pd.DataFrame(),
            'kurt': pd.DataFrame()
        }
        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            if len(today_data):
                today_data['rtn'] = today_data['close'] / today_data['open'] - 1
                today_data['label'] = today_data['datetime'].apply(lambda x: x - relativedelta(minutes=1) if (x.strftime('%M') in ['01', '31']) else None)
                today_data['label'].fillna(method='ffill', inplace=True)

                res = pd.DataFrame(today_data.groupby('label').apply(self._cal))
                res['mean'] = res[0].apply(lambda x: x['mean'])
                res['std'] = res[0].apply(lambda x: x['std'])
                res['skew'] = res[0].apply(lambda x: x['skew'])
                res['kurt'] = res[0].apply(lambda x: x['kurt'])
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


class HFUpDownFactor(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.up_rtn_mean = []
        self.up_rtn_std = []
        self.up_move_vol_pct = []
        self.up_vol_pct = []

        self.down_rtn_mean = []
        self.down_rtn_std = []
        self.down_move_vol_pct = []
        self.down_vol_pct = []

        self.trend_ratio = []

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

            self.exchange.contract_dict[comm].renew_main_contract(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[comm].renew_operate_contract(now_date=self.agent.earth_calender.now_date)
            open_comm_list.append(comm)

        t_factor_dict = self.t_daily_factor(open_comm_list)

        self.up_rtn_mean.append(t_factor_dict['up_rtn_mean'])
        self.up_rtn_std.append(t_factor_dict['up_rtn_std'])
        self.up_move_vol_pct.append(t_factor_dict['up_move_vol_pct'])
        self.up_vol_pct.append(t_factor_dict['up_vol_pct'])

        self.down_rtn_mean.append(t_factor_dict['down_rtn_mean'])
        self.down_rtn_std.append(t_factor_dict['down_rtn_std'])
        self.down_move_vol_pct.append(t_factor_dict['down_move_vol_pct'])
        self.down_vol_pct.append(t_factor_dict['down_vol_pct'])

        self.trend_ratio.append(t_factor_dict['trend_ratio'])

    def _cal(self, x):
        x['mv'] = x['move'] * x['vol']
        up_rtn_mean = x.loc[x['rtn'] > 0, 'rtn'].mean() if len(x.loc[x['rtn'] > 0, 'rtn']) > 0 else 0
        up_rtn_std = x.loc[x['rtn'] > 0, 'rtn'].std(ddof=1) if len(x.loc[x['rtn'] > 0, 'rtn']) > 0 else 0
        up_move_vol_pct = x.loc[x['move'] > 0, 'mv'].sum() / x['mv'].abs().sum() if \
            (len(x.loc[x['move'] > 0]) > 0) & (x['mv'].abs().sum() > 0) else 0
        up_vol_pct = x.loc[x['move'] > 0, 'vol'].sum() / x['vol'].sum() if \
            (len(x.loc[x['vol'] > 0]) > 0) & (x['vol'].sum() > 0) else 0

        down_rtn_mean = x.loc[x['rtn'] < 0, 'rtn'].mean() if len(x.loc[x['rtn'] < 0, 'rtn']) > 0 else 0
        down_rtn_std = x.loc[x['rtn'] < 0, 'rtn'].std(ddof=1) if len(x.loc[x['rtn'] < 0, 'rtn']) > 0 else 0
        down_move_vol_pct = x.loc[x['move'] < 0, 'mv'].sum() / x['mv'].abs().sum() if \
            (len(x.loc[x['move'] < 0]) > 0) & (x['mv'].abs().sum() > 0) else 0
        down_vol_pct = x.loc[x['move'] < 0, 'vol'].sum() / x['move'].sum() if \
            (len(x.loc[x['vol'] > 0]) < 0) & (x['vol'].sum() > 0) else 0

        trend_ratio = x['move'].sum() / x['move'].abs().sum() if x['move'].abs().sum() > 0 else 0

        return {
            'up_rtn_mean': up_rtn_mean,
            'up_rtn_std': up_rtn_std,
            'up_move_vol_pct': up_move_vol_pct,
            'up_vol_pct': up_vol_pct,

            'down_rtn_mean': down_rtn_mean,
            'down_rtn_std': down_rtn_std,
            'down_move_vol_pct': down_move_vol_pct,
            'down_vol_pct': down_vol_pct,

            'trend_ratio': trend_ratio
        }

    def t_daily_factor(self, open_comm_list):

        _factor_dict = {
            'up_rtn_mean': pd.DataFrame(),
            'up_rtn_std': pd.DataFrame(),
            'up_move_vol_pct': pd.DataFrame(),
            'up_vol_pct': pd.DataFrame(),

            'down_rtn_mean': pd.DataFrame(),
            'down_rtn_std': pd.DataFrame(),
            'down_move_vol_pct': pd.DataFrame(),
            'down_vol_pct': pd.DataFrame(),

            'trend_ratio': pd.DataFrame()
        }

        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            if len(today_data):
                today_data['rtn'] = today_data['close'] / today_data['open'] - 1
                today_data['move'] = today_data['close'] - today_data['open']
                today_data['label'] = today_data['datetime'].apply(
                    lambda x: x - relativedelta(minutes=1) if (x.strftime('%M') in ['01', '31']) else None
                )

                today_data['label'].fillna(method='ffill', inplace=True)

                res = pd.DataFrame(today_data.groupby('label').apply(self._cal))

                res['up_rtn_mean'] = res[0].apply(lambda x: x['up_rtn_mean'])
                res['up_rtn_std'] = res[0].apply(lambda x: x['up_rtn_std'])
                res['up_move_vol_pct'] = res[0].apply(lambda x: x['up_move_vol_pct'])
                res['up_vol_pct'] = res[0].apply(lambda x: x['up_vol_pct'])

                res['down_rtn_mean'] = res[0].apply(lambda x: x['down_rtn_mean'])
                res['down_rtn_std'] = res[0].apply(lambda x: x['down_rtn_std'])
                res['down_move_vol_pct'] = res[0].apply(lambda x: x['down_move_vol_pct'])
                res['down_vol_pct'] = res[0].apply(lambda x: x['down_vol_pct'])

                res['trend_ratio'] = res[0].apply(lambda x: x['trend_ratio'])

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


class HFVolPrice(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.dvol_rtn_corr = []
        self.doi_rtn_corr = []
        self.dvol_doi_corr = []

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

            self.exchange.contract_dict[comm].renew_main_contract(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[comm].renew_operate_contract(now_date=self.agent.earth_calender.now_date)
            open_comm_list.append(comm)

        t_factor_dict = self.t_daily_factor(open_comm_list)

        self.dvol_rtn_corr.append(t_factor_dict['dvol_rtn_corr'])
        self.doi_rtn_corr.append(t_factor_dict['doi_rtn_corr'])
        self.dvol_doi_corr.append(t_factor_dict['dvol_doi_corr'])

    def t_daily_factor(self, open_comm_list):

        _factor_dict = {
            'dvol_rtn_corr': pd.DataFrame(),
            'doi_rtn_corr': pd.DataFrame(),
            'dvol_doi_corr': pd.DataFrame()
        }

        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            if len(today_data):
                # 半小时分隔
                today_data['label'] = today_data['datetime'].apply(
                    lambda x: x - relativedelta(minutes=1) if (x.strftime('%M') in ['01', '31']) else None
                )
                today_data['label'].fillna(method='ffill', inplace=True)

                today_data['rtn'] = today_data['close'] / today_data['open'] - 1
                today_data['dvol'] = today_data['volume'] - today_data['volume'].shift(1)
                today_data['doi'] = today_data['open_interest'] - today_data['open_interest'].shift(1)

                res = pd.DataFrame(today_data.groupby('label').apply(self._cal))

                res['dvol_rtn_corr'] = res[0].apply(lambda x: x['dvol_rtn_corr'])
                res['doi_rtn_corr'] = res[0].apply(lambda x: x['doi_rtn_corr'])
                res['dvol_doi_corr'] = res[0].apply(lambda x: x['dvol_doi_corr'])

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

        x.dropna(subset=['rtn', 'dvol', 'doi'], how='any', inplace=True)
        if len(x):
            dvol_rtn_corr, doi_rtn_corr, dvol_doi_corr = \
                x['dvol'].corr(x['rtn']), x['doi'].corr(x['rtn']), x['dvol'].corr(x['doi'])
        else:
            dvol_rtn_corr, doi_rtn_corr, dvol_doi_corr = None, None, None

        return {
            'dvol_rtn_corr': dvol_rtn_corr,
            'doi_rtn_corr': doi_rtn_corr,
            'dvol_doi_corr': dvol_doi_corr
        }


class HFPCAFactor(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.d_first_com = []
        self.d_sec_com = []
        self.first_com_range = []
        self.sec_com_range = []
        self.d_first_com_std = []
        self.d_sec_com_std = []
        self.first_explained_ratio = []
        self.sec_explained_ratio = []

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

            self.exchange.contract_dict[comm].renew_main_contract(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[comm].renew_operate_contract(now_date=self.agent.earth_calender.now_date)
            open_comm_list.append(comm)

        t_factor_dict = self.t_daily_factor(open_comm_list)

        self.d_first_com.append(t_factor_dict['d_first_com'])
        self.d_sec_com.append(t_factor_dict['d_sec_com'])
        self.first_com_range.append(t_factor_dict['first_com_range'])
        self.sec_com_range.append(t_factor_dict['sec_com_range'])
        self.d_first_com_std.append(t_factor_dict['d_first_com_std'])
        self.d_sec_com_std.append(t_factor_dict['d_sec_com_std'])
        self.first_explained_ratio.append(t_factor_dict['first_explained_ratio'])
        self.sec_explained_ratio.append(t_factor_dict['sec_explained_ratio'])

    def t_daily_factor(self, open_comm_list) -> dict:

        _factor_dict = {
            'd_first_com': pd.DataFrame(),
            'd_sec_com': pd.DataFrame(),
            'first_com_range': pd.DataFrame(),
            'sec_com_range': pd.DataFrame(),
            'd_first_com_std': pd.DataFrame(),
            'd_sec_com_std': pd.DataFrame(),
            'first_explained_ratio': pd.DataFrame(),
            'sec_explained_ratio': pd.DataFrame(),
        }

        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            if len(today_data):
                # 半小时分隔
                today_data['label'] = today_data['datetime'].apply(
                    lambda x: x - relativedelta(minutes=1) if (x.strftime('%M') in ['01', '31']) else None
                )
                today_data['label'].fillna(method='ffill', inplace=True)

                today_data['rtn'] = today_data['close'] / today_data['open'] - 1

                res = pd.DataFrame(today_data.groupby('label').apply(self._cal))

                res['d_first_com'] = res[0].apply(lambda x: x['d_first_com'])
                res['d_sec_com'] = res[0].apply(lambda x: x['d_sec_com'])
                res['first_com_range'] = res[0].apply(lambda x: x['first_com_range'])
                res['sec_com_range'] = res[0].apply(lambda x: x['sec_com_range'])
                res['d_first_com_std'] = res[0].apply(lambda x: x['d_first_com_std'])
                res['d_sec_com_std'] = res[0].apply(lambda x: x['d_sec_com_std'])
                res['first_explained_ratio'] = res[0].apply(lambda x: x['first_explained_ratio'])
                res['sec_explained_ratio'] = res[0].apply(lambda x: x['sec_explained_ratio'])

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
        data = x[['open', 'high', 'low', 'close', 'volume', 'open_interest', 'total_turnover']].copy()
        for col in ['open', 'high', 'low', 'close', 'volume', 'open_interest', 'total_turnover']:
            data[col] = (data[col] - data[col].mean()) / data[col].std(ddof=1) if data[col].std(ddof=1) != 0 else 0

        pca = PCA(n_components=3)
        new_x = pca.fit_transform(data)
        com_df = pd.DataFrame(new_x)

        d_first_com = com_df[0].iloc[-1] - com_df[0].iloc[0]
        d_sec_com = com_df[1].iloc[-1] - com_df[1].iloc[0]
        first_com_range = (com_df[0].max() - com_df[0].min())
        sec_com_range = (com_df[1].max() - com_df[1].min())
        d_first_com_std = (com_df[0] - com_df[0].shift(1)).std(ddof=1)
        d_sec_com_std = (com_df[1] - com_df[1].shift(1)).std(ddof=1)
        first_explained_ratio = pca.explained_variance_ratio_[0]
        sec_explained_ratio = pca.explained_variance_ratio_[1]

        return {
            'd_first_com': d_first_com,
            'd_sec_com': d_sec_com,
            'first_com_range': first_com_range,
            'sec_com_range': sec_com_range,
            'd_first_com_std': d_first_com_std,
            'd_sec_com_std': d_sec_com_std,
            'first_explained_ratio': first_explained_ratio,
            'sec_explained_ratio': sec_explained_ratio
        }


class HFBigFactor(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.vbig_rtn_mean = []
        self.vbig_rtn_vol = []
        self.vbig_rv_corr = []

        self.abig_rtn_mean = []
        self.abig_rtn_vol = []
        self.abig_ra_corr = []

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

            self.exchange.contract_dict[comm].renew_main_contract(now_date=self.agent.earth_calender.now_date)
            self.exchange.contract_dict[comm].renew_operate_contract(now_date=self.agent.earth_calender.now_date)
            open_comm_list.append(comm)

        t_factor_dict = self.t_daily_factor(open_comm_list)

        self.vbig_rtn_mean.append(t_factor_dict['vbig_rtn_mean'])
        self.vbig_rtn_vol.append(t_factor_dict['vbig_rtn_vol'])
        self.vbig_rv_corr.append(t_factor_dict['vbig_rv_corr'])
        self.abig_rtn_mean.append(t_factor_dict['abig_rtn_mean'])
        self.abig_rtn_vol.append(t_factor_dict['abig_rtn_vol'])
        self.abig_ra_corr.append(t_factor_dict['abig_ra_corr'])


    def t_daily_factor(self, open_comm_list) -> dict:

        _factor_dict = {
            'vbig_rtn_mean': pd.DataFrame(),
            'vbig_rtn_vol': pd.DataFrame(),
            'vbig_rv_corr': pd.DataFrame(),
            'abig_rtn_mean': pd.DataFrame(),
            'abig_rtn_vol': pd.DataFrame(),
            'abig_ra_corr': pd.DataFrame(),
        }

        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            if len(today_data):
                # 半小时分隔
                today_data['label'] = today_data['datetime'].apply(
                    lambda x: x - relativedelta(minutes=1) if (x.strftime('%M') in ['01', '31']) else None
                )
                today_data['label'].fillna(method='ffill', inplace=True)

                today_data['rtn'] = today_data['close'] / today_data['open'] - 1
                today_data['amt'] = today_data['close'] * today_data['volume']

                res = pd.DataFrame(today_data.groupby('label').apply(self._cal))

                res['vbig_rtn_mean'] = res[0].apply(lambda x: x['vbig_rtn_mean'])
                res['vbig_rtn_vol'] = res[0].apply(lambda x: x['vbig_rtn_vol'])
                res['vbig_rv_corr'] = res[0].apply(lambda x: x['vbig_rv_corr'])
                res['abig_rtn_mean'] = res[0].apply(lambda x: x['abig_rtn_mean'])
                res['abig_rtn_vol'] = res[0].apply(lambda x: x['abig_rtn_vol'])
                res['abig_ra_corr'] = res[0].apply(lambda x: x['abig_ra_corr'])

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
        vbig_cond = x['volume'] > x['volume'].quantile(0.5)
        abig_cond = x['amt'] > x['amt'].quantile(0.5)

        vbig_rtn_mean = x.loc[vbig_cond, 'rtn'].mean() if len(x.loc[vbig_cond]) else 0
        vbig_rtn_vol = x.loc[vbig_cond, 'rtn'].std(ddof=1) if len(x.loc[vbig_cond]) else 0
        vbig_rv_corr = x.loc[vbig_cond, ['rtn', 'volume']].corr().iloc[0, 1] if len(x.loc[vbig_cond]) else 0

        abig_rtn_mean = x.loc[abig_cond, 'rtn'].mean() if len(x.loc[abig_cond]) else 0
        abig_rtn_vol = x.loc[abig_cond, 'rtn'].std(ddof=1) if len(x.loc[abig_cond]) else 0
        abig_ra_corr = x.loc[abig_cond, ['rtn', 'amt']].corr().iloc[0, 1] if len(x.loc[abig_cond]) else 0


        return {
            'vbig_rtn_mean': vbig_rtn_mean,
            'vbig_rtn_vol': vbig_rtn_vol,
            'vbig_rv_corr': vbig_rv_corr,
            'abig_rtn_mean': abig_rtn_mean,
            'abig_rtn_vol': abig_rtn_vol,
            'abig_ra_corr': abig_ra_corr,
        }


if __name__ == '__main__':
    cal_factor = HFPCAFactor(
        factor_name='moment',
        begin_date='2020-01-04',
        end_date='2020-01-10',
        init_cash=1000000,
        contract_list=NORMAL_CONTRACT_INFO[:3],
        local_data_path=local_data_path
    )
    cal_factor.test()
