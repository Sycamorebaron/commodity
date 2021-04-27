from factor.test.main_test import MainTest
from utils.base_para import *
import pandas as pd
from sklearn.decomposition import PCA
import numpy as np
from dateutil.relativedelta import relativedelta
import statsmodels.api as sm

pd.set_option('expand_frame_repr', False)


class FactorTest(MainTest):
    def _daily_process(self):
        pass

    def trunc_data(self, _data):
        today_data = _data.loc[_data['datetime'].apply(
            lambda x: x.strftime('%Y-%m-%d') == self.agent.earth_calender.now_date.strftime('%Y-%m-%d')
        )].copy()
        return today_data

    def _trunc_data(self, _data):

        cond1 = _data['datetime'] >= self.agent.earth_calender.now_date - relativedelta(days=4)
        cond2 = _data['datetime'] < self.agent.earth_calender.now_date + relativedelta(days=1)
        today_data = _data.loc[cond1 & cond2].copy()
        today_data.reset_index(drop=True, inplace=True)

        return today_data

    def test(self):
        while not self.agent.earth_calender.end_of_test():
            # 交易日
            if self.exchange.trade_calender.tradable_date(date=self.agent.earth_calender.now_date):
                self._daily_process()

            self.agent.earth_calender.next_day()


class RtnMoment(FactorTest):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.mean = []
        self.std = []
        self.skew = []
        self.kurt = []
        self.factor_name = factor_name

    def _daily_process(self):
        print(self.agent.earth_calender.now_date)
        tem_mean = {'date': self.agent.earth_calender.now_date}
        tem_std = {'date': self.agent.earth_calender.now_date}
        tem_skew = {'date': self.agent.earth_calender.now_date}
        tem_kurt = {'date': self.agent.earth_calender.now_date}
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

            tem_mean[comm], tem_std[comm], tem_skew[comm], tem_kurt[comm] = self.t_factor(comm)

        if (int(self.agent.earth_calender.now_date.strftime('%m')) >= 12) & (
                int(self.agent.earth_calender.now_date.strftime('%d')) >= 25):
            mean = pd.DataFrame(self.mean)
            std = pd.DataFrame(self.std)
            skew = pd.DataFrame(self.skew)
            kurt = pd.DataFrame(self.kurt)
            mean.to_excel(
                os.path.join(OUTPUT_DATA_PATH, '%s_mean.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            std.to_excel(
                os.path.join(OUTPUT_DATA_PATH, '%s_std.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            skew.to_excel(
                os.path.join(OUTPUT_DATA_PATH, '%s_skew.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            kurt.to_excel(
                os.path.join(OUTPUT_DATA_PATH, '%s_kurt.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )

        self.mean.append(tem_mean)
        self.std.append(tem_std)
        self.skew.append(tem_skew)
        self.kurt.append(tem_kurt)

    def t_factor(self, comm):

        now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
        today_data = self.trunc_data(_data)

        today_data['rtn'] = today_data['close'] / today_data['open'] - 1
        return today_data['rtn'].mean(), today_data['rtn'].std(ddof=1), today_data['rtn'].skew(), today_data['rtn'].kurtosis()


class RtnFactor(FactorTest):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.first_5T_rtn = []
        self.first_10T_rtn = []
        self.first_30T_rtn = []
        self.last_5T_rtn = []
        self.last_10T_rtn = []
        self.last_30T_rtn = []

    def _daily_process(self):
        print(self.agent.earth_calender.now_date)
        tem_first_5t = {'date': self.agent.earth_calender.now_date}
        tem_first_10t = {'date': self.agent.earth_calender.now_date}
        tem_first_30t = {'date': self.agent.earth_calender.now_date}
        tem_last_5t = {'date': self.agent.earth_calender.now_date}
        tem_last_10t = {'date': self.agent.earth_calender.now_date}
        tem_last_30t = {'date': self.agent.earth_calender.now_date}

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

            tem_first_5t[comm], tem_first_10t[comm], tem_first_30t[comm], tem_last_5t[comm], tem_last_10t[
                comm], tem_last_30t[comm] = self.t_factor(comm)

        self.first_5T_rtn.append(tem_first_5t)
        self.first_10T_rtn.append(tem_first_10t)
        self.first_30T_rtn.append(tem_first_30t)

        self.last_5T_rtn.append(tem_last_5t)
        self.last_10T_rtn.append(tem_last_10t)
        self.last_30T_rtn.append(tem_last_30t)

        if (int(self.agent.earth_calender.now_date.strftime('%m')) >= 12) & (
                int(self.agent.earth_calender.now_date.strftime('%d')) >= 25):

            first_5t = pd.DataFrame(self.first_5T_rtn)
            first_10t = pd.DataFrame(self.first_10T_rtn)
            first_30t = pd.DataFrame(self.first_30T_rtn)
            last_5t = pd.DataFrame(self.last_5T_rtn)
            last_10t = pd.DataFrame(self.last_10T_rtn)
            last_30t = pd.DataFrame(self.last_30T_rtn)

            first_5t.to_excel(
                os.path.join(OUTPUT_DATA_PATH, '%s_first_5t.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            first_10t.to_excel(
                os.path.join(OUTPUT_DATA_PATH, '%s_first_10t.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            first_30t.to_excel(
                os.path.join(OUTPUT_DATA_PATH, '%s_first_30t.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )

            last_5t.to_excel(
                os.path.join(OUTPUT_DATA_PATH, '%s_last_5t.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            last_10t.to_excel(
                os.path.join(OUTPUT_DATA_PATH, '%s_last_10t.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            last_30t.to_excel(
                os.path.join(OUTPUT_DATA_PATH, '%s_last_30t.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )

    def t_factor(self, comm):

        now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
        today_data = self.trunc_data(_data)

        # use only day data
        today_data = today_data.loc[today_data['datetime'].apply(lambda x: int(x.strftime('%H')) <= 15)]

        today_data = today_data.resample(on='datetime', rule='5T').agg(
            {
                'order_book_id': 'last',
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum',
                'open_interest': 'last',
                'total_turnover': 'sum'
            }
        )
        today_data.reset_index(inplace=True)

        first_5t_rtn = today_data['close'].iloc[0] / today_data['open'].iloc[0] - 1
        first_10t_rtn = today_data['close'].iloc[1] / today_data['open'].iloc[0] - 1
        first_30t_rtn = today_data['close'].iloc[5] / today_data['open'].iloc[0] - 1

        last_5t_rtn = today_data['close'].iloc[-1] / today_data['open'].iloc[-1] - 1
        last_10t_rtn = today_data['close'].iloc[-1] / today_data['open'].iloc[-2] - 1
        last_30t_rtn = today_data['close'].iloc[-1] / today_data['open'].iloc[-5] - 1

        return first_5t_rtn, first_10t_rtn, first_30t_rtn, last_5t_rtn, last_10t_rtn, last_30t_rtn


class MomentumFactor(FactorTest):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.up_move_pct = []
        self.except_last_30t = []

    def _daily_process(self):
        print(self.agent.earth_calender.now_date)
        tem_up_move_pct = {'date': self.agent.earth_calender.now_date}
        tem_except_last_30t = {'date': self.agent.earth_calender.now_date}

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

            tem_up_move_pct[comm], tem_except_last_30t[comm] = self.t_factor(comm=comm)

        self.up_move_pct.append(tem_up_move_pct)
        self.except_last_30t.append(tem_except_last_30t)

        if (int(self.agent.earth_calender.now_date.strftime('%m')) >= 12) & (
            int(self.agent.earth_calender.now_date.strftime('%d')) >= 25):
            t_up_move_pct = pd.DataFrame(self.up_move_pct)
            t_except_last_30t = pd.DataFrame(self.except_last_30t)

            t_up_move_pct.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_up_move_pct.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            t_except_last_30t.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_except_last_30t.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )

    def t_factor(self, comm):

        now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
        today_data = self.trunc_data(_data)

        today_data = today_data.loc[today_data['datetime'].apply(lambda x: int(x.strftime('%H')) <= 15)]
        today_data.reset_index(inplace=True)

        today_data['move'] = (today_data['close'] - today_data['open']).apply(lambda x: abs(x))
        up_move = today_data.loc[today_data['close'] > today_data['open'], 'move'].sum()
        all_move = today_data['move'].sum()
        up_move_pct = up_move / all_move if all_move else 0

        except_last_30t = today_data['close'].iloc[-30] / today_data['open'].iloc[0]
        return up_move_pct, except_last_30t


class VolAmtSplit(FactorTest):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.morning_vol_pct = []
        self.down_vol_pct = []
        self.open_30t_vol_pct = []
        self.last_30t_vol_pct =[]
        self.open_30t_close_30t_vol = []
        self.morning_afternoon_vol = []

        self.morning_amt_pct = []
        self.down_amt_pct = []
        self.open_30t_amt_pct = []
        self.last_30t_amt_pct =[]
        self.open_30t_close_30t_amt = []
        self.morning_afternoon_amt = []

    def _daily_process(self):
        print(self.agent.earth_calender.now_date)
        tem_morning_vol_pct = {'date': self.agent.earth_calender.now_date}
        tem_down_vol_pct = {'date': self.agent.earth_calender.now_date}
        tem_open_30t_vol_pct = {'date': self.agent.earth_calender.now_date}
        tem_last_30t_vol_pct = {'date': self.agent.earth_calender.now_date}
        tem_open_30t_close_30t_vol = {'date': self.agent.earth_calender.now_date}
        tem_morning_afternoon_vol = {'date': self.agent.earth_calender.now_date}

        tem_morning_amt_pct = {'date': self.agent.earth_calender.now_date}
        tem_down_amt_pct = {'date': self.agent.earth_calender.now_date}
        tem_open_30t_amt_pct = {'date': self.agent.earth_calender.now_date}
        tem_last_30t_amt_pct = {'date': self.agent.earth_calender.now_date}
        tem_open_30t_close_30t_amt = {'date': self.agent.earth_calender.now_date}
        tem_morning_afternoon_amt = {'date': self.agent.earth_calender.now_date}

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

            tem_morning_vol_pct[comm], tem_down_vol_pct[comm], tem_open_30t_vol_pct[comm], tem_last_30t_vol_pct[comm], \
            tem_open_30t_close_30t_vol[comm], tem_morning_afternoon_vol[comm], tem_morning_amt_pct[comm], \
            tem_down_amt_pct[comm], tem_open_30t_amt_pct[comm], tem_last_30t_amt_pct[comm], \
            tem_open_30t_close_30t_amt[comm], tem_morning_afternoon_amt[comm] = self.t_factor(comm=comm)

        self.morning_vol_pct.append(tem_morning_vol_pct)
        self.down_vol_pct.append(tem_down_vol_pct)
        self.open_30t_vol_pct.append(tem_open_30t_vol_pct)
        self.last_30t_vol_pct.append(tem_last_30t_vol_pct)
        self.open_30t_close_30t_vol.append(tem_open_30t_close_30t_vol)
        self.morning_afternoon_vol.append(tem_morning_afternoon_vol)

        self.morning_amt_pct.append(tem_morning_amt_pct)
        self.down_amt_pct.append(tem_down_amt_pct)
        self.open_30t_amt_pct.append(tem_open_30t_amt_pct)
        self.last_30t_amt_pct.append(tem_last_30t_amt_pct)
        self.open_30t_close_30t_amt.append(tem_open_30t_close_30t_amt)
        self.morning_afternoon_amt.append(tem_morning_afternoon_amt)


        if (int(self.agent.earth_calender.now_date.strftime('%m')) >= 12) & (
            int(self.agent.earth_calender.now_date.strftime('%d')) >= 25):

            t_morning_vol_pct = pd.DataFrame(self.morning_vol_pct)
            t_down_vol_pct = pd.DataFrame(self.down_vol_pct)
            t_open_30t_vol_pct = pd.DataFrame(self.open_30t_vol_pct)
            t_last_30t_vol_pct = pd.DataFrame(self.last_30t_vol_pct)
            t_open_30t_close_30t_vol = pd.DataFrame(self.open_30t_close_30t_vol)
            t_morning_afternoon_vol = pd.DataFrame(self.morning_afternoon_vol)

            t_morning_amt_pct = pd.DataFrame(self.morning_amt_pct)
            t_down_amt_pct = pd.DataFrame(self.down_amt_pct)
            t_open_30t_amt_pct = pd.DataFrame(self.open_30t_amt_pct)
            t_last_30t_amt_pct = pd.DataFrame(self.last_30t_amt_pct)
            t_open_30t_close_30t_amt = pd.DataFrame(self.open_30t_close_30t_amt)
            t_morning_afternoon_amt = pd.DataFrame(self.morning_afternoon_amt)

            t_morning_vol_pct.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_morning_vol_pct.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            t_down_vol_pct.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_down_vol_pct.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            t_open_30t_vol_pct.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_open_30t_vol_pct.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            t_last_30t_vol_pct.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_last_30t_vol_pct.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            t_open_30t_close_30t_vol.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_open_30t_close_30t_vol.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            t_morning_afternoon_vol.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_morning_afternoon_vol.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            t_morning_amt_pct.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_morning_amt_pct.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            t_down_amt_pct.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_down_amt_pct.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            t_open_30t_amt_pct.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_open_30t_amt_pct.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            t_last_30t_amt_pct.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_last_30t_amt_pct.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            t_open_30t_close_30t_amt.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_open_30t_close_30t_amt.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            t_morning_afternoon_amt.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_morning_afternoon_amt.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )

    def t_factor(self, comm):
        now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
        today_data = self.trunc_data(_data)

        # use only day data
        today_data = today_data.loc[today_data['datetime'].apply(lambda x: int(x.strftime('%H')) <= 15)]
        today_data.reset_index(inplace=True)

        today_data['amt'] = today_data['volume'] * today_data['close']

        vol_sum = today_data['volume'].sum()
        amt_sum = today_data['amt'].sum()

        morning_vol = today_data.loc[
            today_data['datetime'].apply(lambda x: int(x.strftime('%H')) <= 12), 'volume'
        ].sum()
        morning_amount = today_data.loc[
            today_data['datetime'].apply(lambda x: int(x.strftime('%H')) <= 12), 'amt'
        ].sum()

        morning_vol_pct = morning_vol / vol_sum if vol_sum != 0 else 0
        morning_amt_pct = morning_amount / amt_sum if amt_sum != 0 else 0

        down_vol_pct = today_data.loc[today_data['close'] > today_data['open'], 'volume'
                       ].sum() / vol_sum if vol_sum != 0 else 0
        down_amt_pct = today_data.loc[today_data['close'] > today_data['open'], 'amt'
                       ].sum() / amt_sum if amt_sum != 0 else 0

        open_30t_vol_pct = today_data[:6]['volume'].sum() / vol_sum if vol_sum != 0 else 0
        open_30t_amt_pct = today_data[:6]['amt'].sum() / amt_sum if amt_sum != 0 else 0

        last_30t_vol_pct = today_data[-6:]['volume'].sum() / vol_sum if vol_sum != 0 else 0
        last_30t_amt_pct = today_data[-6:]['amt'].sum() / amt_sum if amt_sum != 0 else 0

        open_30t_close_30t_vol = today_data[:6]['volume'].sum() / today_data[-6:]['volume'].sum() \
            if today_data[-6:]['volume'].sum() != 0 else 0
        open_30t_close_30t_amt = today_data[:6]['amt'].sum() / today_data[-6:]['amt'].sum() \
            if today_data[-6:]['amt'].sum() != 0 else 0

        morning_afternoon_vol = morning_vol_pct / (1 - morning_vol_pct) if morning_vol_pct != 1 else 0
        morning_afternoon_amt = morning_amt_pct / (1 - morning_amt_pct) if morning_amt_pct != 1 else 0

        return morning_vol_pct, down_vol_pct, open_30t_vol_pct, last_30t_vol_pct, open_30t_close_30t_vol, \
               morning_afternoon_vol, morning_amt_pct, down_amt_pct, open_30t_amt_pct, last_30t_amt_pct, \
               open_30t_close_30t_amt, morning_afternoon_amt


class VolPrice(FactorTest):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.dvol_rtn_corr = []
        self.doi_rtn_corr = []
        self.dvol_doi_corr = []

    def _daily_process(self):
        print(self.agent.earth_calender.now_date)
        tem_dvol_rtn_corr = {'date': self.agent.earth_calender.now_date}
        tem_doi_rtn_corr = {'date': self.agent.earth_calender.now_date}
        tem_dvol_doi_corr = {'date': self.agent.earth_calender.now_date}

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

            tem_dvol_rtn_corr[comm], tem_doi_rtn_corr[comm], tem_dvol_doi_corr[comm] = self.t_factor(comm)

        self.dvol_rtn_corr.append(tem_dvol_rtn_corr)
        self.doi_rtn_corr.append(tem_doi_rtn_corr)
        self.dvol_doi_corr.append(tem_dvol_doi_corr)

        if (int(self.agent.earth_calender.now_date.strftime('%m')) >= 12) & (
                int(self.agent.earth_calender.now_date.strftime('%d')) >= 25):
            dvol_corr = pd.DataFrame(self.dvol_rtn_corr)
            doi_corr = pd.DataFrame(self.doi_rtn_corr)
            dvol_doi_corr = pd.DataFrame(self.dvol_doi_corr)

            dvol_corr.to_excel(
                os.path.join(OUTPUT_DATA_PATH, '%s_dvol_corr.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            doi_corr.to_excel(
                os.path.join(OUTPUT_DATA_PATH, '%s_doi_corr.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            dvol_doi_corr.to_excel(
                os.path.join(
                    OUTPUT_DATA_PATH, '%s_dvol_doi_corr.xlsx' % self.agent.earth_calender.now_date.strftime('%Y')
                )
            )

    def t_factor(self, comm):
        now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
        today_data = self.trunc_data(_data)

        today_data['rtn'] = today_data['close'] / today_data['close'].shift(1) - 1
        today_data['dvol'] = today_data['volume'] / today_data['volume'].shift(1) - 1
        today_data['doi'] = today_data['open_interest'] / today_data['open_interest'].shift(1) - 1
        corr_df = today_data[['rtn', 'dvol', 'doi']].corr()

        dvol_rtn = corr_df.loc[corr_df.index == 'dvol', 'rtn'].values[0]
        doi_rtn = corr_df.loc[corr_df.index == 'doi', 'rtn'].values[0]
        dvol_doi = corr_df.loc[corr_df.index == 'dvol', 'doi'].values[0]
        return dvol_rtn, doi_rtn, dvol_doi


class MoneyFlow(FactorTest):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.money_flow = []

    def _daily_process(self):
        print(self.agent.earth_calender.now_date)
        tem_money_flow = {'date': self.agent.earth_calender.now_date}

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

            tem_money_flow[comm] = self.t_factor(comm)

        self.money_flow.append(tem_money_flow)

        if (int(self.agent.earth_calender.now_date.strftime('%m')) >= 12) & (
                int(self.agent.earth_calender.now_date.strftime('%d')) >= 25):
            money_flow = pd.DataFrame(self.money_flow)

            money_flow.to_excel(
                os.path.join(OUTPUT_DATA_PATH, '%s_money_flow.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
 
    def t_factor(self, comm):
        now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
        today_data = self.trunc_data(_data)

        up_cond = today_data['close'] > today_data['open']
        down_cond = today_data['close'] < today_data['open']
        today_data['_close'] = 0
        today_data.loc[up_cond, '_close'] = today_data['close']
        today_data.loc[down_cond, '_close'] = -today_data['close']
        money_flow = (today_data['_close'] * today_data['volume']).sum() / \
                     (today_data['close'] * today_data['volume']).sum() if today_data['volume'].sum() != 0 else 0

        return money_flow


class BasisFactor(FactorTest):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.main_sec_basis = []
        self.open_basis = []
        self.close_basis = []
        self.main_sec_basis_rv = []
        self.mean_basis = []

    def _daily_process(self):
        print(self.agent.earth_calender.now_date)
        tem_main_sec_basis = {'date': self.agent.earth_calender.now_date}
        tem_main_sec_basis_rv = {'date': self.agent.earth_calender.now_date}
        tem_open_basis = {'date': self.agent.earth_calender.now_date}
        tem_close_basis = {'date': self.agent.earth_calender.now_date}
        tem_mean_basis = {'date': self.agent.earth_calender.now_date}

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

            tem_main_sec_basis[comm], tem_main_sec_basis_rv[comm], tem_open_basis[comm], tem_close_basis[comm], \
            tem_mean_basis[comm]= self.t_factor(comm)

        self.main_sec_basis.append(tem_main_sec_basis)
        self.main_sec_basis_rv.append(tem_main_sec_basis_rv)
        self.open_basis.append(tem_open_basis)
        self.close_basis.append(tem_close_basis)
        self.mean_basis.append(tem_mean_basis)

        if (int(self.agent.earth_calender.now_date.strftime('%m')) >= 12) & (
                int(self.agent.earth_calender.now_date.strftime('%d')) >= 25):
            main_sec_basis = pd.DataFrame(self.main_sec_basis)
            main_sec_basis_rv = pd.DataFrame(self.main_sec_basis_rv)
            open_basis = pd.DataFrame(self.open_basis)
            close_basis = pd.DataFrame(self.close_basis)
            mean_basis = pd.DataFrame(self.mean_basis)

            main_sec_basis.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_main_sec_basis.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            main_sec_basis_rv.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_main_sec_basis_rv.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            open_basis.to_csv(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_open_basis.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            close_basis.to_csv(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_close_basis.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            mean_basis.to_csv(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_mean_basis.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )

    def t_factor(self, comm):
        now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        now_sec_main_contract = self.exchange.contract_dict[comm].now_sec_main_contract(
            now_date=self.agent.earth_calender.now_date
        )

        if (now_sec_main_contract == '') or  (now_main_contract == ''):
            return np.nan, np.nan, np.nan, np.nan, np.nan

        _main_data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
        _sec_data = self.exchange.contract_dict[comm].data_dict[now_sec_main_contract]

        today_main = self.trunc_data(_main_data).reset_index(drop=True)
        today_sec_main = self.trunc_data(_sec_data).reset_index(drop=True)

        today_main['sec'] = today_sec_main['close']
        today_main['basis'] = today_main['sec'] / today_main['close'] - 1

        basis_rv = today_main['basis'].std(ddof=1)
        basis = today_main['basis'].iloc[-1]
        open_basis = today_main['basis'][:6].mean()
        close_basis = today_main['basis'][-6:].mean()
        mean_basis = today_main['basis'].mean()

        return basis, basis_rv, open_basis, close_basis, mean_basis


class PCAFactor(FactorTest):
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
        tem_d_first_com = {'date': self.agent.earth_calender.now_date}
        tem_d_sec_com = {'date': self.agent.earth_calender.now_date}
        tem_first_com_range = {'date': self.agent.earth_calender.now_date}
        tem_sec_com_range = {'date': self.agent.earth_calender.now_date}
        tem_d_first_com_std = {'date': self.agent.earth_calender.now_date}
        tem_d_sec_com_std = {'date': self.agent.earth_calender.now_date}
        tem_first_explained_ratio = {'date': self.agent.earth_calender.now_date}
        tem_sec_explained_ratio = {'date': self.agent.earth_calender.now_date}

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

            tem_d_first_com[comm], tem_d_sec_com[comm], tem_first_com_range[comm], tem_sec_com_range[comm], \
            tem_d_first_com_std[comm], tem_d_sec_com_std[comm], tem_first_explained_ratio[comm], \
            tem_sec_explained_ratio[comm] = self.t_factor(comm)

        self.d_first_com.append(tem_d_first_com)
        self.d_sec_com.append(tem_d_sec_com)
        self.first_com_range.append(tem_first_com_range)
        self.sec_com_range.append(tem_sec_com_range)
        self.d_first_com_std.append(tem_d_first_com_std)
        self.d_sec_com_std.append(tem_d_sec_com_std)
        self.first_explained_ratio.append(tem_first_explained_ratio)
        self.sec_explained_ratio.append(tem_sec_explained_ratio)

        if (int(self.agent.earth_calender.now_date.strftime('%m')) >= 12) & (
                int(self.agent.earth_calender.now_date.strftime('%d')) >= 25):
            d_first_com = pd.DataFrame(self.d_first_com)
            d_sec_com = pd.DataFrame(self.d_sec_com)
            first_com_range = pd.DataFrame(self.first_com_range)
            sec_com_range = pd.DataFrame(self.sec_com_range)
            d_first_com_std = pd.DataFrame(self.d_first_com_std)
            d_sec_com_std = pd.DataFrame(self.d_sec_com_std)
            first_explained_ratio = pd.DataFrame(self.first_explained_ratio)
            sec_explained_ratio = pd.DataFrame(self.sec_explained_ratio)

            d_first_com.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_first_com_rtn.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            d_sec_com.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_sec_com_rtn.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            first_com_range.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_first_com_range.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            sec_com_range.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_sec_com_range.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            d_first_com_std.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_first_com_rtn_std.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            d_sec_com_std.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_sec_com_rtn_std.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            first_explained_ratio.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_first_explained_ratio.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            sec_explained_ratio.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_sec_explained_ratio.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )

    def t_factor(self, comm):
        now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        _main_data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
        today_data = self.trunc_data(_main_data)

        data = today_data[['open', 'high', 'low', 'close', 'volume', 'open_interest', 'total_turnover']].copy()
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

        return d_first_com, d_sec_com, first_com_range, sec_com_range, d_first_com_std, d_sec_com_std, \
               first_explained_ratio, sec_explained_ratio


class UpDownFactor(FactorTest):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.up_rtn_var = []
        self.down_rtn_var = []
        self.up_vol_pct = []
        self.up_amt_pct = []
        self.trend_ratio = []  # 日内价格变化/分钟频价格变化绝对值

    def _daily_process(self):
        print(self.agent.earth_calender.now_date)
        tem_up_rtn_var = {'date': self.agent.earth_calender.now_date}
        tem_down_rtn_var = {'date': self.agent.earth_calender.now_date}
        tem_up_vol_pct = {'date': self.agent.earth_calender.now_date}
        tem_up_amt_pct = {'date': self.agent.earth_calender.now_date}
        tem_trend_ratio = {'date': self.agent.earth_calender.now_date}


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

            tem_up_rtn_var[comm], tem_down_rtn_var[comm], tem_up_vol_pct[comm], tem_up_amt_pct[comm], \
            tem_trend_ratio[comm] = self.t_factor(comm)

        self.up_rtn_var.append(tem_up_rtn_var)
        self.down_rtn_var.append(tem_down_rtn_var)
        self.up_vol_pct.append(tem_up_vol_pct)
        self.up_amt_pct.append(tem_up_amt_pct)
        self.trend_ratio.append(tem_trend_ratio)


        if (int(self.agent.earth_calender.now_date.strftime('%m')) >= 12) & (
                int(self.agent.earth_calender.now_date.strftime('%d')) >= 25):
            up_rtn_var = pd.DataFrame(self.up_rtn_var)
            down_rtn_var = pd.DataFrame(self.down_rtn_var)
            up_vol_pct = pd.DataFrame(self.up_vol_pct)
            up_amt_pct = pd.DataFrame(self.up_amt_pct)
            trend_ratio = pd.DataFrame(self.trend_ratio)

            up_rtn_var.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_up_rtn_var.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            down_rtn_var.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_down_rtn_var.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            up_vol_pct.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_up_vol_pct.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            up_amt_pct.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_up_amt_pct.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            trend_ratio.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_trend_ratio.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )

    def t_factor(self, comm):
        now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
        today_data = self.trunc_data(_data)

        today_data = today_data.loc[today_data['datetime'].apply(lambda x: int(x.strftime('%H')) <= 15)]
        today_data.reset_index(inplace=True)

        today_data['rtn'] = today_data['close'] / today_data['open'] - 1
        up_rtn_cond = today_data['close'] > today_data['open']
        down_rtn_cond = today_data['close'] < today_data['open']
        up_rtn_var = today_data.loc[up_rtn_cond, 'rtn'].std(ddof=1) if len(today_data.loc[up_rtn_cond]) else 0
        down_rtn_var = today_data.loc[down_rtn_cond, 'rtn'].std(ddof=1) if len(today_data.loc[down_rtn_cond]) else 0

        today_data['amt'] = today_data['close'] * today_data['volume']
        up_vol_pct = today_data.loc[up_rtn_cond, 'volume'].sum() / today_data['volume'].sum() \
            if len(today_data.loc[up_rtn_cond]) else 0
        up_amt_pct = today_data.loc[up_rtn_cond, 'amt'].sum() / today_data['amt'].sum() \
            if len(today_data.loc[up_rtn_cond]) else 0
        trend_ratio = (today_data['close'] - today_data['open']).abs().sum() / \
                      (today_data['close'].iloc[-1] - today_data['open'].iloc[0]) if \
            (today_data['close'].iloc[-1] != today_data['open'].iloc[0]) else 0

        return up_rtn_var, down_rtn_var, up_vol_pct, up_amt_pct, trend_ratio


class BigFactor(FactorTest):
    # 大单
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
        tem_vbig_rtn_mean = {'date': self.agent.earth_calender.now_date}
        tem_vbig_rtn_vol = {'date': self.agent.earth_calender.now_date}
        tem_vbig_rv_corr = {'date': self.agent.earth_calender.now_date}

        tem_abig_rtn_mean = {'date': self.agent.earth_calender.now_date}
        tem_abig_rtn_vol = {'date': self.agent.earth_calender.now_date}
        tem_abig_ra_corr = {'date': self.agent.earth_calender.now_date}

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

            tem_vbig_rtn_mean[comm], tem_vbig_rtn_vol[comm], tem_vbig_rv_corr[comm], tem_abig_rtn_mean[comm], \
            tem_abig_rtn_vol[comm], tem_abig_ra_corr[comm] = self.t_factor(comm)

        self.vbig_rtn_mean.append(tem_vbig_rtn_mean)
        self.vbig_rtn_vol.append(tem_vbig_rtn_vol)
        self.vbig_rv_corr.append(tem_vbig_rv_corr)
        self.abig_rtn_mean.append(tem_abig_rtn_mean)
        self.abig_rtn_vol.append(tem_abig_rtn_vol)
        self.abig_ra_corr.append(tem_abig_ra_corr)


        if (int(self.agent.earth_calender.now_date.strftime('%m')) >= 12) & (
                int(self.agent.earth_calender.now_date.strftime('%d')) >= 25):
            vbig_rtn_mean = pd.DataFrame(self.vbig_rtn_mean)
            vbig_rtn_vol = pd.DataFrame(self.vbig_rtn_vol)
            vbig_rv_corr = pd.DataFrame(self.vbig_rv_corr)

            abig_rtn_mean = pd.DataFrame(self.abig_rtn_mean)
            abig_rtn_vol = pd.DataFrame(self.abig_rtn_vol)
            abig_ra_corr = pd.DataFrame(self.abig_ra_corr)

            vbig_rtn_mean.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_vbig_rtn_mean.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            vbig_rtn_vol.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_vbig_rtn_vol.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            vbig_rv_corr.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_vbig_rv_corr.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            abig_rtn_mean.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_abig_rtn_mean.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            abig_rtn_vol.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_abig_rtn_vol.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            abig_ra_corr.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_abig_ra_corr.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )

    def t_factor(self, comm):
        now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
        today_data = self.trunc_data(_data)

        today_data = today_data.loc[today_data['datetime'].apply(lambda x: int(x.strftime('%H')) <= 15)]
        today_data.reset_index(inplace=True)
        today_data['amt'] = today_data['close'] * today_data['volume']
        today_data['rtn'] = today_data['close'] / today_data['open'] - 1

        vbig_cond = today_data['volume'] > today_data['volume'].quantile(0.67)
        abig_cond = today_data['amt'] > today_data['amt'].quantile(0.67)

        vbig_rtn_mean = today_data.loc[vbig_cond, 'rtn'].mean() if len(today_data.loc[vbig_cond]) else 0
        vbig_rtn_vol = today_data.loc[vbig_cond, 'rtn'].std(ddof=1) if len(today_data.loc[vbig_cond]) else 0
        vbig_rv_vorr = today_data.loc[vbig_cond, ['rtn', 'volume']].corr().iloc[0, 1] \
            if len(today_data.loc[vbig_cond]) else 0

        abig_rtn_mean = today_data.loc[abig_cond, 'rtn'].mean() if len(today_data.loc[abig_cond]) else 0
        abig_rtn_vol = today_data.loc[abig_cond, 'rtn'].std(ddof=1) if len(today_data.loc[abig_cond]) else 0
        abig_ra_corr = today_data.loc[abig_cond, ['rtn', 'amt']].corr().iloc[0, 1] \
            if len(today_data.loc[abig_cond]) else 0

        return vbig_rtn_mean, vbig_rtn_vol, vbig_rv_vorr, abig_rtn_mean, abig_rtn_vol, abig_ra_corr


class Liquidity(FactorTest):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.amihud = []
        self.roll_spread = []
        self.LOT = []
        self.pastor_gamma = []

    def _daily_process(self):
        print(self.agent.earth_calender.now_date)
        tem_amihud = {'date': self.agent.earth_calender.now_date}
        tem_roll_spread = {'date': self.agent.earth_calender.now_date}
        tem_LOT = {'date': self.agent.earth_calender.now_date}
        tem_pastor_gamma = {'date': self.agent.earth_calender.now_date}

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

            tem_amihud[comm], tem_roll_spread[comm], tem_LOT[comm], tem_pastor_gamma[comm] = self.t_factor(comm)

        self.amihud.append(tem_amihud)
        self.roll_spread.append(tem_roll_spread)
        self.LOT.append(tem_LOT)
        self.pastor_gamma.append(tem_pastor_gamma)

        if (int(self.agent.earth_calender.now_date.strftime('%m')) >= 12) & (
                int(self.agent.earth_calender.now_date.strftime('%d')) >= 25):
            amihud = pd.DataFrame(self.amihud)
            roll_spread = pd.DataFrame(self.roll_spread)
            LOT = pd.DataFrame(self.LOT)
            pastor_gamma = pd.DataFrame(self.pastor_gamma)

            amihud.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_amihud.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            roll_spread.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_roll_spread.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            LOT.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_LOT.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            pastor_gamma.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_pastor_gamma.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )

    def t_factor(self, comm):
        now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
        today_data = self.trunc_data(_data)

        today_data = today_data.loc[today_data['datetime'].apply(lambda x: int(x.strftime('%H')) <= 15)]
        today_data.reset_index(inplace=True)
        today_data['amt'] = today_data['close'] * today_data['volume']

        amihud = abs(today_data['close'].iloc[-1] / today_data['open'].iloc[0] - 1) / today_data['amt'].sum() \
            if today_data['amt'].sum() > 0 else 0
        today_data['dp'] = today_data['close'] - today_data['close'].shift(1)
        today_data['dp_1'] = today_data['dp'].shift(1)
        _d = today_data[1:].copy()
        cov = _d['dp'].cov(_d['dp_1'])
        roll_spread = -2 * np.sqrt(-cov) if cov < 0 else 0
        LOT = len(today_data.loc[today_data['open'] == today_data['close']]) / len(today_data)

        today_data['rtn'] = today_data['close'] / today_data['open'] - 1
        today_data['x'] = (today_data['rtn'].apply(lambda x : 1 if x >= 0 else -1) * today_data['volume']).shift(1)
        x = today_data[1:]['x'].copy()
        y = today_data[1:]['rtn'].copy()
        model = sm.OLS(endog=y, exog=x)
        res = model.fit()
        pastor_gamma = dict(res.params)['x']

        return amihud, roll_spread, LOT, pastor_gamma


class SingularVol(FactorTest):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.BV = []
        self.BV_sigma = []
        self.bollerslev_RSJ =[]

    def _daily_process(self):
        print(self.agent.earth_calender.now_date)
        tem_BV = {'date': self.agent.earth_calender.now_date}
        tem_BV_sigma = {'date': self.agent.earth_calender.now_date}
        tem_bollerslev_RSJ = {'date': self.agent.earth_calender.now_date}

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

            tem_BV[comm], tem_BV_sigma[comm], tem_bollerslev_RSJ[comm] = self.t_factor(comm)

        self.BV.append(tem_BV)
        self.BV_sigma.append(tem_BV_sigma)
        self.bollerslev_RSJ.append(tem_bollerslev_RSJ)

        if (int(self.agent.earth_calender.now_date.strftime('%m')) >= 12) & (
                int(self.agent.earth_calender.now_date.strftime('%d')) >= 25):
            BV = pd.DataFrame(self.BV)
            BV_sigma = pd.DataFrame(self.BV_sigma)
            bollerslev_RSJ = pd.DataFrame(self.bollerslev_RSJ)

            BV.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_BV.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            BV_sigma.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_BV_sigma.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            bollerslev_RSJ.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_bollerslev_RSJ.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )


    def t_factor(self, comm):
        now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
        today_data = self.trunc_data(_data)

        today_data = today_data.loc[today_data['datetime'].apply(lambda x: int(x.strftime('%H')) <= 15)]
        today_data.reset_index(inplace=True)

        today_data['rtn'] = today_data['close'] / today_data['open'] - 1
        BV = (today_data['rtn'].abs() * today_data['rtn'].shift(1)).sum() / (len(today_data) - 2)
        BV_sigma = np.sqrt(BV) if BV > 0 else 0

        bollerslev_RSJ = \
            (today_data.loc[today_data['rtn'] > 0, 'rtn'].std(ddof=1) -
             today_data.loc[today_data['rtn'] < 0, 'rtn'].std(ddof=1)) / today_data['rtn'].std(ddof=1) if \
                today_data['rtn'].std(ddof=1) > 0 else 0

        return BV, BV_sigma, bollerslev_RSJ


class Others(FactorTest):
    def __init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path):
        FactorTest.__init__(self, factor_name, begin_date, end_date, init_cash, contract_list, local_data_path)
        self.smart_money_vol_pct = []
        self.CVaR = []
        self.VCVaR = []
        self.vwap_move_pct = []

    def _daily_process(self):
        print(self.agent.earth_calender.now_date)
        tem_smart_money_vol_pct = {'date': self.agent.earth_calender.now_date}
        tem_CVaR = {'date': self.agent.earth_calender.now_date}
        tem_VCVaR = {'date': self.agent.earth_calender.now_date}
        tem_vwap_move_pct = {'date': self.agent.earth_calender.now_date}

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

            tem_smart_money_vol_pct[comm], tem_CVaR[comm], tem_VCVaR[comm], tem_vwap_move_pct[comm] = \
                self.t_factor(comm)

        self.smart_money_vol_pct.append(tem_smart_money_vol_pct)
        self.CVaR.append(tem_CVaR)
        self.VCVaR.append(tem_VCVaR)
        self.vwap_move_pct.append(tem_vwap_move_pct)

        if (int(self.agent.earth_calender.now_date.strftime('%m')) >= 12) & (
                int(self.agent.earth_calender.now_date.strftime('%d')) >= 25):
            smart_money_vol_pct = pd.DataFrame(self.smart_money_vol_pct)
            CVaR = pd.DataFrame(self.CVaR)
            VCVaR = pd.DataFrame(self.VCVaR)
            vwap_move_pct = pd.DataFrame(self.vwap_move_pct)

            smart_money_vol_pct.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_smart_money_vol_pct.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            CVaR.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_CVaR.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            VCVaR.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_VCVaR.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )
            vwap_move_pct.to_excel(
                os.path.join(OUTPUT_DATA_PATH,
                             '%s_vwap_move_pct.xlsx' % self.agent.earth_calender.now_date.strftime('%Y'))
            )

    def t_factor(self, comm):
        now_main_contract = self.exchange.contract_dict[comm].now_main_contract(
            now_date=self.agent.earth_calender.now_date
        )
        _data = self.exchange.contract_dict[comm].data_dict[now_main_contract]
        today_data = self.trunc_data(_data)

        today_data = today_data.loc[today_data['datetime'].apply(lambda x: int(x.strftime('%H')) <= 15)]
        today_data.reset_index(inplace=True)

        today_data['rtn'] = today_data['close'] / today_data['open'] - 1

        today_data['st'] = 0
        today_data.loc[today_data['volume'] != 0, 'st'] = \
            today_data['rtn'].abs() / today_data['volume'].apply(lambda x: np.sqrt(x))
        smart_money_vol_pct = today_data.loc[today_data['st'] >= today_data['st'].quantile(0.7), 'volume'].sum() / \
                              today_data['volume'].sum() if today_data['volume'].sum() != 0 else 0

        cvar = today_data.loc[today_data['rtn'] <= today_data['rtn'].quantile(0.05), 'rtn'].mean()
        today_data['v_rtn'] = today_data['rtn'] * today_data['volume']
        vcvar = today_data.loc[today_data['rtn'] <= today_data['rtn'].quantile(0.05), 'v_rtn'].sum() / \
                today_data.loc[today_data['rtn'] <= today_data['rtn'].quantile(0.05), 'volume'].sum() if today_data.loc[today_data['rtn'] <= today_data['rtn'].quantile(0.05), 'volume'].sum() != 0 else 0

        today_data['move'] = today_data['close'] - today_data['open']
        vwap_move_pct = (today_data['move'] * today_data['volume']).sum() / today_data['volume'].sum() if today_data['volume'].sum() != 0 else 0
        return smart_money_vol_pct, cvar, vcvar, vwap_move_pct