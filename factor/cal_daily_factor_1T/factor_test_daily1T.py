from utils.base_para import *
import pandas as pd
from sklearn.decomposition import PCA
import numpy as np
from dateutil.relativedelta import relativedelta
import statsmodels.api as sm
from factor.cal_factor.factor_test import FactorTest

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

    def trunc_data(self, _data):
        today_data = _data.loc[_data['date'] == self.agent.earth_calender.now_date.strftime('%Y-%m-%d')].copy()
        today_data = today_data.loc[today_data['datetime'].apply(lambda x: int(x.strftime('%H')) < 21)]

        # today_data = _data.loc[_data['datetime'].apply(
        #     lambda x: x.strftime('%Y-%m-%d') == self.agent.earth_calender.now_date.strftime('%Y-%m-%d')
        # )].copy()
        return today_data

    def trunc_data_v2(self, _data, date):
        today_data = _data.loc[_data['date'] == date].copy()
        today_data = today_data.loc[today_data['datetime'].apply(lambda x: int(x.strftime('%H')) < 21)]
        return today_data

    @staticmethod
    def add_label(data):
        data['label'] = data['datetime'].apply(
            # lambda x: x - relativedelta(minutes=1) if (x.strftime('%M') in ['01', '31']) else None
            lambda x: x - relativedelta(minutes=1) if (x.strftime('%M') in ['01', '16', '31', '46']) else None
        )
        data['label'].fillna(method='ffill', inplace=True)
        return data


class HFRtn(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        HFFactor.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.rtn_1d = []

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

        self.rtn_1d.append(daily_rtn_30t)

    def t_daily_factor(self, open_comm_list):

        _rtn_res = {}
        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data).reset_index(drop=True)

            if 'datetime' not in _rtn_res:
                _rtn_res['datetime'] = today_data['datetime'].iloc[-1]

            _rtn_res[comm] = today_data['close'].iloc[-1] / today_data['open'].iloc[0] - 1

        _rtn_df = pd.DataFrame(_rtn_res, index=[0])

        return _rtn_df


class HFContinuousContract(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        HFFactor.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.close_open = []
        self.close_high = []
        self.close_low = []
        self.close_close = []
        self.oi_oi = []
        self.vol_vol = []

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

        self.close_open.append(t_factor_dict['close_open'])
        self.close_high.append(t_factor_dict['close_high'])
        self.close_low.append(t_factor_dict['close_low'])
        self.close_close.append(t_factor_dict['close_close'])
        self.oi_oi.append(t_factor_dict['oi_oi'])
        self.vol_vol.append(t_factor_dict['vol_vol'])

    def t_daily_factor(self, open_comm_list):
        _factor_dict = {
            'close_open': {},
            'close_high': {},
            'close_low': {},
            'close_close': {},
            'oi_oi': {},
            'vol_vol': {},
        }

        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            yesterday_data = self.trunc_data_v2(
                _data=_data,
                date=self.exchange.trade_calender.get_last_trading_date(
                    date=self.agent.earth_calender.now_date
                ).strftime('%Y-%m-%d')
            )
            if len(today_data) & len(yesterday_data):

                today_data = self.add_label(data=today_data)

                res = self._cal(today_data=today_data, yesterday_data=yesterday_data)
                res['datetime'] = today_data['datetime'].iloc[-1]

                for factor in _factor_dict.keys():
                    if 'datetime' not in _factor_dict[factor].keys():
                        _factor_dict[factor]['datetime'] = res['datetime']

                    _factor_dict[factor][comm] = res[factor]

        for factor in _factor_dict.keys():
            _factor_dict[factor] = pd.DataFrame(_factor_dict[factor], index=[0])
        return _factor_dict

    def _cal(self, today_data, yesterday_data):

        yesterday_close = yesterday_data['close'].iloc[-1]
        yesterday_oi = yesterday_data['open_interest'].iloc[-1]
        yesterday_volume = yesterday_data['volume'].sum()

        today_open = today_data['open'].max()
        today_high = today_data['high'].max()
        today_low = today_data['low'].max()
        today_close = today_data['close'].max()
        today_oi = today_data['open_interest'].iloc[-1]
        today_volume = today_data['volume'].sum()

        return {
            'close_open': today_open / yesterday_close - 1,
            'close_high': today_high / yesterday_close - 1,
            'close_low': today_low / yesterday_close - 1,
            'close_close': today_close / yesterday_close - 1,
            'oi_oi': today_oi / yesterday_oi - 1 if yesterday_oi != 0 else 0,
            'vol_vol': today_volume / yesterday_volume - 1 if yesterday_volume != 0 else 0,
        }


class HFMaxMinRtn(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        HFFactor.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.max_rtn = []
        self.min_rtn = []

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

        self.max_rtn.append(t_factor_dict['max_rtn'])
        self.min_rtn.append(t_factor_dict['min_rtn'])

    def t_daily_factor(self, open_comm_list):
        _factor_dict = {
            'max_rtn': {},
            'min_rtn': {},
        }

        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            if len(today_data):

                today_data = self.add_label(data=today_data)
                res = self._cal(today_data)
                res['datetime'] = today_data['datetime'].iloc[-1]

                for factor in _factor_dict.keys():
                    if 'datetime' not in _factor_dict[factor].keys():
                        _factor_dict[factor]['datetime'] = res['datetime']

                    _factor_dict[factor][comm] = res[factor]

        for factor in _factor_dict.keys():
            _factor_dict[factor] = pd.DataFrame(_factor_dict[factor], index=[0])
        return _factor_dict

    def _cal(self, x):
        return {
            'max_rtn': x['high'].max() / x['open'].iloc[0] - 1,
            'min_rtn': x['low'].min() / x['open'].iloc[0] - 1,
        }


class HFRtnMoment(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        HFFactor.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
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
        x['rtn'] = x['close'] / x['open'] - 1

        return {
            'mean': x['rtn'].mean(),
            'std': x['rtn'].std(ddof=1),
            'skew': x['rtn'].skew(),
            'kurt': x['rtn'].kurtosis()
        }

    def t_daily_factor(self, open_comm_list):

        _factor_dict = {
            'mean': {},
            'std': {},
            'skew': {},
            'kurt': {}
        }
        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            if len(today_data):

                today_data = self.add_label(data=today_data)

                res = self._cal(today_data)
                res['datetime'] = today_data['datetime'].iloc[-1]

                for factor in _factor_dict.keys():
                    if 'datetime' not in _factor_dict[factor].keys():
                        _factor_dict[factor]['datetime'] = res['datetime']

                    _factor_dict[factor][comm] = res[factor]

        for factor in _factor_dict.keys():
            _factor_dict[factor] = pd.DataFrame(_factor_dict[factor], index=[0])
        return _factor_dict


class HFUpDownFactor(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        HFFactor.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
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
        x['move'] = (x['close'] - x['open']).abs()
        x['vol'] = x['volume']
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
            'up_rtn_mean': {},
            'up_rtn_std': {},
            'up_move_vol_pct': {},
            'up_vol_pct': {},

            'down_rtn_mean': {},
            'down_rtn_std': {},
            'down_move_vol_pct': {},
            'down_vol_pct': {},

            'trend_ratio': {}
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

                res = self._cal(today_data)
                res['datetime'] = today_data['datetime'].iloc[-1]

                for factor in _factor_dict.keys():
                    if 'datetime' not in _factor_dict[factor].keys():
                        _factor_dict[factor]['datetime'] = res['datetime']

                    _factor_dict[factor][comm] = res[factor]

        for factor in _factor_dict.keys():
            _factor_dict[factor] = pd.DataFrame(_factor_dict[factor], index=[0])
        return _factor_dict


class HFVolPrice(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        HFFactor.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
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
            'dvol_rtn_corr': {},
            'doi_rtn_corr': {},
            'dvol_doi_corr': {}
        }
        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            if len(today_data):

                today_data = self.add_label(data=today_data)
                res = self._cal(today_data)
                res['datetime'] = today_data['datetime'].iloc[-1]

                for factor in _factor_dict.keys():
                    if 'datetime' not in _factor_dict[factor].keys():
                        _factor_dict[factor]['datetime'] = res['datetime']

                    _factor_dict[factor][comm] = res[factor]

        for factor in _factor_dict.keys():
            _factor_dict[factor] = pd.DataFrame(_factor_dict[factor], index=[0])

        return _factor_dict

    def _cal(self, x):
        x['rtn'] = x['close'] / x['open'] - 1
        x['dvol'] = x['volume'] - x['volume'].shift(1)
        x['doi'] = x['open_interest'] - x['open_interest'].shift(1)
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
        HFFactor.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
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
            'd_first_com': {},
            'd_sec_com': {},
            'first_com_range': {},
            'sec_com_range': {},
            'd_first_com_std': {},
            'd_sec_com_std': {},
            'first_explained_ratio': {},
            'sec_explained_ratio': {},
        }
        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            if len(today_data):

                today_data = self.add_label(data=today_data)
                res = self._cal(today_data)
                res['datetime'] = today_data['datetime'].iloc[-1]

                for factor in _factor_dict.keys():
                    if 'datetime' not in _factor_dict[factor].keys():
                        _factor_dict[factor]['datetime'] = res['datetime']

                    _factor_dict[factor][comm] = res[factor]

        for factor in _factor_dict.keys():
            _factor_dict[factor] = pd.DataFrame(_factor_dict[factor], index=[0])
        return _factor_dict

    def _cal(self, x):
        data = x[['open', 'high', 'low', 'close', 'volume', 'open_interest', 'total_turnover']].copy()
        for col in ['open', 'high', 'low', 'close', 'volume', 'open_interest', 'total_turnover']:
            data[col] = (data[col] - data[col].mean()) / data[col].std(ddof=1) if data[col].std(ddof=1) != 0 else 0

        if x['volume'].sum() == 0:
            print(x)
            return {
                'd_first_com': 0,
                'd_sec_com': 0,
                'first_com_range': 0,
                'sec_com_range': 0,
                'd_first_com_std': 0,
                'd_sec_com_std': 0,
                'first_explained_ratio': 0,
                'sec_explained_ratio': 0
            }

        if data['volume'].sum() > 0:
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

        else:
            d_first_com = 0
            d_sec_com = 0
            first_com_range = 0
            sec_com_range = 0
            d_first_com_std = 0
            d_sec_com_std = 0
            first_explained_ratio = 0
            sec_explained_ratio = 0

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
        HFFactor.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
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
            'vbig_rtn_mean': {},
            'vbig_rtn_vol': {},
            'vbig_rv_corr': {},
            'abig_rtn_mean': {},
            'abig_rtn_vol': {},
            'abig_ra_corr': {},
        }
        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)

            if len(today_data):

                today_data = self.add_label(data=today_data)
                res = self._cal(today_data)
                res['datetime'] = today_data['datetime'].iloc[-1]

                for factor in _factor_dict.keys():
                    if 'datetime' not in _factor_dict[factor].keys():
                        _factor_dict[factor]['datetime'] = res['datetime']

                    _factor_dict[factor][comm] = res[factor]

        for factor in _factor_dict.keys():
            _factor_dict[factor] = pd.DataFrame(_factor_dict[factor], index=[0])
        return _factor_dict

    def _cal(self, x):

        x['amt'] = x['close'] * x['volume']
        x['rtn'] = x['close'] / x['open'] - 1
        vbig_cond = x['volume'] >= x['volume'].quantile(0.5)
        abig_cond = x['amt'] >= x['amt'].quantile(0.5)

        vbig_rtn_mean = x.loc[vbig_cond, 'rtn'].mean() if len(x.loc[vbig_cond]) else None
        vbig_rtn_vol = x.loc[vbig_cond, 'rtn'].std(ddof=1) if len(x.loc[vbig_cond]) else None
        vbig_rv_corr = x.loc[vbig_cond, ['rtn', 'volume']].corr().iloc[0, 1] if len(x.loc[vbig_cond]) else None

        abig_rtn_mean = x.loc[abig_cond, 'rtn'].mean() if len(x.loc[abig_cond]) else None
        abig_rtn_vol = x.loc[abig_cond, 'rtn'].std(ddof=1) if len(x.loc[abig_cond]) else None
        abig_ra_corr = x.loc[abig_cond, ['rtn', 'amt']].corr().iloc[0, 1] if len(x.loc[abig_cond]) else None


        return {
            'vbig_rtn_mean': vbig_rtn_mean,
            'vbig_rtn_vol': vbig_rtn_vol,
            'vbig_rv_corr': vbig_rv_corr,
            'abig_rtn_mean': abig_rtn_mean,
            'abig_rtn_vol': abig_rtn_vol,
            'abig_ra_corr': abig_ra_corr,
        }


class HFLiquidity(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        HFFactor.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.amihud = []
        self.roll_spread = []
        self.LOT = []
        self.pastor_gamma = []

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

        self.amihud.append(t_factor_dict['amihud'])
        self.roll_spread.append(t_factor_dict['roll_spread'])
        self.LOT.append(t_factor_dict['LOT'])
        self.pastor_gamma.append(t_factor_dict['pastor_gamma'])

    def t_daily_factor(self, open_comm_list) -> dict:

        _factor_dict = {
            'amihud': {},
            'roll_spread': {},
            'LOT': {},
            'pastor_gamma': {}
        }

        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            if len(today_data):

                res = self._cal(today_data)
                res['datetime'] = today_data['datetime'].iloc[-1]


                for factor in _factor_dict.keys():
                    if 'datetime' not in _factor_dict[factor].keys():
                        _factor_dict[factor]['datetime'] = res['datetime']

                    _factor_dict[factor][comm] = res[factor]

        for factor in _factor_dict.keys():
            _factor_dict[factor] = pd.DataFrame(_factor_dict[factor], index=[0])

        return _factor_dict

    def _cal(self, x):
        x['amt'] = x['close'] * x['volume']
        x['rtn'] = x['close'] / x['open'] - 1
        amihud = abs(x['close'].iloc[-1] / x['open'].iloc[0] - 1) / x['amt'].sum()
        LOT = len(x.loc[x['open'] == x['close']]) / len(x)

        x['dp'] = x['close'] - x['close'].shift(1)
        x['dp_1'] = x['dp'].shift(1)
        _d = x[1:].copy()
        cov = _d['dp'].cov(_d['dp_1'])
        roll_spread = -2 * np.sqrt(-cov) if cov < 0 else 0

        x['rtn'] = x['close'] / x['open'] - 1
        x['x'] = (x['rtn'].apply(lambda x : 1 if x >= 0 else -1) * x['volume']).shift(1)
        X = x[1:]['x'].copy()
        Y = x[1:]['rtn'].copy()
        model = sm.OLS(endog=Y, exog=X)
        res = model.fit()
        pastor_gamma = dict(res.params)['x']

        return {
            'amihud': amihud,
            'roll_spread': roll_spread,
            'LOT': LOT,
            'pastor_gamma': pastor_gamma,
        }


class HFSingularFactor(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        HFFactor.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.BV = []
        self.BV_sigma = []
        self.bollerslev_RSJ =[]

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

        self.BV.append(t_factor_dict['BV'])
        self.BV_sigma.append(t_factor_dict['BV_sigma'])
        self.bollerslev_RSJ.append(t_factor_dict['bollerslev_RSJ'])

    def t_daily_factor(self, open_comm_list) -> dict:

        _factor_dict = {
            'BV': {},
            'BV_sigma': {},
            'bollerslev_RSJ': {}
        }

        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            if len(today_data):

                today_data = self.add_label(data=today_data)

                res = self._cal(today_data)
                res['datetime'] = today_data['datetime'].iloc[-1]

                for factor in _factor_dict.keys():
                    if 'datetime' not in _factor_dict[factor].keys():
                        _factor_dict[factor]['datetime'] = res['datetime']

                    _factor_dict[factor][comm] = res[factor]

        for factor in _factor_dict.keys():
            _factor_dict[factor] = pd.DataFrame(_factor_dict[factor], index=[0])
        return _factor_dict

    def _cal(self, x):
        x['rtn'] = x['close'] / x['open'] - 1
        x['lrtn'] = x['close'].apply(lambda q: np.log(q)) - x['open'].apply(lambda q: np.log(q))
        BV = (x['lrtn'].abs() * x['lrtn'].shift(1)).sum() / (len(x) - 2)
        BV_sigma = np.sqrt(BV) if BV > 0 else None
        bollerslev_RSJ = \
            (x.loc[x['rtn'] > 0, 'rtn'].std(ddof=1) -
             x.loc[x['rtn'] < 0, 'rtn'].std(ddof=1)) / x['rtn'].std(ddof=1) if \
                x['rtn'].std(ddof=1) > 0 else 0

        return {
            'BV': BV,
            'BV_sigma': BV_sigma,
            'bollerslev_RSJ': bollerslev_RSJ
        }


class HFSimplePriceVolumeFactor(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        HFFactor.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.highest_rtn = []
        self.lowest_rtn = []
        self.range_pct = []
        self.vol_oi = []
        self.d_oi = []

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

        self.highest_rtn.append(t_factor_dict['highest_rtn'])
        self.lowest_rtn.append(t_factor_dict['lowest_rtn'])
        self.range_pct.append(t_factor_dict['range_pct'])
        self.vol_oi.append(t_factor_dict['vol_oi'])
        self.d_oi.append(t_factor_dict['d_oi'])

    def t_daily_factor(self, open_comm_list) -> dict:

        _factor_dict = {
            'highest_rtn': {},
            'lowest_rtn': {},
            'range_pct': {},
            'vol_oi': {},
            'd_oi': {},
        }

        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            if len(today_data):

                today_data = self.add_label(data=today_data)

                res = self._cal(today_data)
                res['datetime'] = today_data['datetime'].iloc[-1]

                for factor in _factor_dict.keys():
                    if 'datetime' not in _factor_dict[factor].keys():
                        _factor_dict[factor]['datetime'] = res['datetime']

                    _factor_dict[factor][comm] = res[factor]

        for factor in _factor_dict.keys():
            _factor_dict[factor] = pd.DataFrame(_factor_dict[factor], index=[0])
        return _factor_dict

    def _cal(self, x):
        x['rtn'] = x['close'] / x['open'] - 1

        highest_rtn = x['high'].max() / x['open'].iloc[0] - 1
        lowest_rtn = x['low'].min() / x['open'].iloc[0] - 1
        range_pct = x['high'].max() / x['low'].min() - 1
        vol_oi = x['volume'].sum() / x['open_interest'].iloc[0]
        d_oi = x['open_interest'].iloc[-1] / x['open_interest'].iloc[0] - 1

        return {
            'highest_rtn': highest_rtn,
            'lowest_rtn': lowest_rtn,
            'range_pct': range_pct,
            'vol_oi': vol_oi,
            'd_oi': d_oi,
        }


class HFPVCorrFactor(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        HFFactor.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.P1V0 = []
        self.P2V0 = []
        self.P3V0 = []
        self.P0V1 = []
        self.P0V2 = []
        self.P0V3 = []

        self.R1DV0 = []
        self.R2DV0 = []
        self.R3DV0 = []
        self.R0DV1 = []
        self.R0DV2 = []
        self.R0DV3 = []

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

        self.P1V0.append(t_factor_dict['P1V0'])
        self.P2V0.append(t_factor_dict['P2V0'])
        self.P3V0.append(t_factor_dict['P3V0'])
        self.P0V1.append(t_factor_dict['P0V1'])
        self.P0V2.append(t_factor_dict['P0V2'])
        self.P0V3.append(t_factor_dict['P0V3'])

        self.R1DV0.append(t_factor_dict['R1DV0'])
        self.R2DV0.append(t_factor_dict['R2DV0'])
        self.R3DV0.append(t_factor_dict['R3DV0'])
        self.R0DV1.append(t_factor_dict['R0DV1'])
        self.R0DV2.append(t_factor_dict['R0DV2'])
        self.R0DV3.append(t_factor_dict['R0DV3'])

    def t_daily_factor(self, open_comm_list) -> dict:

        _factor_dict = {
            'P1V0': {},
            'P2V0': {},
            'P3V0': {},
            'P0V1': {},
            'P0V2': {},
            'P0V3': {},

            'R1DV0': {},
            'R2DV0': {},
            'R3DV0': {},
            'R0DV1': {},
            'R0DV2': {},
            'R0DV3': {},
        }

        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            if len(today_data):

                today_data = self.add_label(data=today_data)
                res = self._cal(today_data)
                res['datetime'] = today_data['datetime'].iloc[-1]

                for factor in _factor_dict.keys():
                    if 'datetime' not in _factor_dict[factor].keys():
                        _factor_dict[factor]['datetime'] = res['datetime']

                    _factor_dict[factor][comm] = res[factor]

        for factor in _factor_dict.keys():
            _factor_dict[factor] = pd.DataFrame(_factor_dict[factor], index=[0])
        return _factor_dict

    def _cal(self, x):
        x['rtn'] = x['close'] / x['open'] - 1
        x['dv'] = x['volume'] - x['volume'].shift(1)
        steady_cond_1 = (x['close'].std(ddof=1) == 0) or (x['volume'].std(ddof=1) == 0)
        if steady_cond_1:
            P1V0, P2V0, P3V0, P0V1, P0V2, P0V3 = 0, 0, 0, 0, 0, 0
        else:
            P1V0 = x['close'].shift(1).corr(x['volume'])
            P2V0 = x['close'].shift(2).corr(x['volume'])
            P3V0 = x['close'].shift(3).corr(x['volume'])
            P0V1 = x['close'].shift(-1).corr(x['volume'])
            P0V2 = x['close'].shift(-2).corr(x['volume'])
            P0V3 = x['close'].shift(-3).corr(x['volume'])

        steady_cond_2 = (x['rtn'].std(ddof=1) == 0) or (x['dv'].std(ddof=1) == 0)
        if steady_cond_2:
            R1DV0, R2DV0, R3DV0, R0DV1, R0DV2, R0DV3 = 0, 0, 0, 0, 0, 0
        else:
            R1DV0 = x['rtn'].shift(1).corr(x['dv'])
            R2DV0 = x['rtn'].shift(2).corr(x['dv'])
            R3DV0 = x['rtn'].shift(3).corr(x['dv'])
            R0DV1 = x['rtn'].shift(-1).corr(x['dv'])
            R0DV2 = x['rtn'].shift(-2).corr(x['dv'])
            R0DV3 = x['rtn'].shift(-3).corr(x['dv'])

        return {
            'P1V0': P1V0,
            'P2V0': P2V0,
            'P3V0': P3V0,
            'P0V1': P0V1,
            'P0V2': P0V2,
            'P0V3': P0V3,

            'R1DV0': R1DV0,
            'R2DV0': R2DV0,
            'R3DV0': R3DV0,
            'R0DV1': R0DV1,
            'R0DV2': R0DV2,
            'R0DV3': R0DV3,
        }


class HFVolumeRatioFactor(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        HFFactor.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.open_5t_pct = []
        self.open_15t_pct = []
        self.open_30t_pct = []
        self.close_5t_pct = []
        self.close_15t_pct = []
        self.close_30t_pct = []

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

        self.open_5t_pct.append(t_factor_dict['open_5t_pct'])
        self.open_15t_pct.append(t_factor_dict['open_15t_pct'])
        self.open_30t_pct.append(t_factor_dict['open_30t_pct'])
        self.close_5t_pct.append(t_factor_dict['close_5t_pct'])
        self.close_15t_pct.append(t_factor_dict['close_15t_pct'])
        self.close_30t_pct.append(t_factor_dict['close_30t_pct'])

    def t_daily_factor(self, open_comm_list) -> dict:

        _factor_dict = {
            'open_5t_pct': {},
            'open_15t_pct': {},
            'open_30t_pct': {},
            'close_5t_pct': {},
            'close_15t_pct': {},
            'close_30t_pct': {}
        }
        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            if len(today_data):

                today_data = self.add_label(data=today_data)
                res = self._cal(today_data)
                res['datetime'] = today_data['datetime'].iloc[-1]

                for factor in _factor_dict.keys():
                    if 'datetime' not in _factor_dict[factor].keys():
                        _factor_dict[factor]['datetime'] = res['datetime']

                    _factor_dict[factor][comm] = res[factor]

        for factor in _factor_dict.keys():
            _factor_dict[factor] = pd.DataFrame(_factor_dict[factor], index=[0])
        return _factor_dict

    def _cal(self, x):
        if not len(x):
            return {
                'open_5t_pct': None,
                'open_15t_pct': None,
                'open_30t_pct': None,
                'close_5t_pct': None,
                'close_15t_pct': None,
                'close_30t_pct': None,
            }
        else:
            x.reset_index(drop=True, inplace=True)


            return {
                'open_5t_pct': x[:5]['volume'].sum() / x['volume'].sum()
                if x['volume'].sum() != 0 else 0,
                'open_15t_pct': x[:15]['volume'].sum() / x['volume'].sum()
                if x['volume'].sum() != 0 else 0,
                'open_30t_pct': x[:30]['volume'].sum() / x['volume'].sum()
                if x['volume'].sum() != 0 else 0,
                'close_5t_pct': x[-5:]['volume'].sum() / x['volume'].sum()
                if x['volume'].sum() != 0 else 0,
                'close_15t_pct': x[-15:]['volume'].sum() / x['volume'].sum()
                if x['volume'].sum() != 0 else 0,
                'close_30t_pct': x[-30:]['volume'].sum() / x['volume'].sum()
                if x['volume'].sum() != 0 else 0,
            }


class HFLeverageEffect(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        HFFactor.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.BV_rtn = []
        self.std_rtn = []

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

        self.BV_rtn.append(t_factor_dict['BV_rtn'])
        self.std_rtn.append(t_factor_dict['std_rtn'])

    def t_daily_factor(self, open_comm_list) -> dict:

        _factor_dict = {
            'BV_rtn': {},
            'std_rtn': {},
        }
        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            today_data = self.trunc_data(_data)
            if len(today_data):

                today_data = self.add_label(data=today_data)

                res = self._cal(today_data)
                res['datetime'] = today_data['datetime'].iloc[-1]

                for factor in _factor_dict.keys():
                    if 'datetime' not in _factor_dict[factor].keys():
                        _factor_dict[factor]['datetime'] = res['datetime']

                    _factor_dict[factor][comm] = res[factor]

        for factor in _factor_dict.keys():
            _factor_dict[factor] = pd.DataFrame(_factor_dict[factor], index=[0])
        return _factor_dict

    def _cal(self, x):
        x['rtn'] = x['close'] / x['open'] - 1

        if not len(x):
            return {
                'BV_rtn': None,
                'std_rtn': None,
            }
        else:
            x.reset_index(drop=True, inplace=True)

            x['BV'] = x['rtn'].abs() * x['rtn'].shift(1).abs() / (len(x) - 2)
            x['std'] = x['rtn'].rolling(30).std(ddof=1)
            x = x[30:].reset_index(drop=True)

            return {
                'BV_rtn': x['rtn'].corr(x['BV']),
                'std_rtn': x['rtn'].corr(x['std']),
            }


class HFBasisFactor(HFFactor):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        HFFactor.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.main_sec_basis = []
        self.d_main_sec_basis = []
        self.dbdv = []
        self.dbdoi = []

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

        self.main_sec_basis.append(t_factor_dict['main_sec_basis'])
        self.d_main_sec_basis.append(t_factor_dict['d_main_sec_basis'])
        self.dbdv.append(t_factor_dict['dbdv'])
        self.dbdoi.append(t_factor_dict['dbdoi'])


    def t_daily_factor(self, open_comm_list) -> dict:

        _factor_dict = {
            'main_sec_basis': {},
            'd_main_sec_basis': {},
            'dbdv': {},
            'dbdoi': {},
        }

        for comm in open_comm_list:
            now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            now_sec_main_contract = self.exchange.contract_dict[comm].now_sec_main_contract(
                now_date=self.agent.earth_calender.now_date
            )
            if now_sec_main_contract == '':
                continue

            _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
            _sec_data = self.exchange.contract_dict[comm].data_dict[now_sec_main_contract]

            today_data = self.trunc_data(_data)
            today_sec_data = self.trunc_data(_sec_data).reset_index(drop=True)
            today_data['rtn'] = today_data['close'] / today_data['open'] - 1
            today_data['sec'] = today_sec_data['close']
            today_data['sec_v'] = today_sec_data['volume']
            today_data['sec_oi'] = today_sec_data['open_interest']

            if len(today_data):

                today_data = self.add_label(data=today_data)
                res = self._cal(today_data)
                res['datetime'] = today_data['datetime'].iloc[-1]

                for factor in _factor_dict.keys():
                    if 'datetime' not in _factor_dict[factor].keys():
                        _factor_dict[factor]['datetime'] = res['datetime']

                    _factor_dict[factor][comm] = res[factor]

        for factor in _factor_dict.keys():
            _factor_dict[factor] = pd.DataFrame(_factor_dict[factor], index=[0])
        return _factor_dict

    def _cal(self, x):

        x['basis_rate'] = x['close'] / x['sec'] - 1
        x['basis'] = x['close'] - x['sec']
        x['db'] = x['basis'] - x['basis'].shift(1)
        x['dv'] = (x['volume'] + x['sec_v']) - (x['volume'] + x['sec_v']).shift(1)
        x['doi'] = (x['open_interest'] + x['sec_oi']) - (x['open_interest'] + x['sec_oi']).shift(1)

        return {
            'main_sec_basis': x['basis_rate'].iloc[-1],
            'd_main_sec_basis': x['basis'].iloc[-1] / x['basis'].iloc[0] - 1 if x['basis'].iloc[0] != 0 else None,
            'dbdv': x['db'].corr(x['dv']),
            'dbdoi': x['db'].corr(x['doi']),
        }


if __name__ == '__main__':
    cal_factor = HFRtn(
        factor_name='moment',
        begin_date='2011-01-01',
        end_date='2011-02-28',
        init_cash=1000000,
        contract_list=[i for i in NORMAL_CONTRACT_INFO if i['id'] in ['L', 'M', 'C']],
        # contract_list=NORMAL_CONTRACT_INFO,
        local_data_path=local_data_path
    )
    cal_factor.test()
    rtn_1d_df = pd.concat(cal_factor.rtn_1d).reset_index(drop=True)

    print(rtn_1d_df)
