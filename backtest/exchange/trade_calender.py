import pandas as pd
from utils.base_para import *
from datetime import timedelta


class TradeCalender:
    def __init__(self):
        self.is_trade_date = False
        self._date = self.date_stream_init()

    @staticmethod
    def date_stream_init():
        sql = 'select * from "public"."szzs"'
        d = pd.read_sql_query(sql, con=eg)
        d = d[['date', 'close']].copy()
        d['date'] = pd.to_datetime(d['date'])
        return d

    # 检查传入的时间是否可交易
    def tradable_date(self, date):
        date = pd.to_datetime(date)
        if date in list(self._date['date'].values):
            return True
        else:
            return False

    # 根据交易日找下一个交易日
    def get_next_trading_date(self, date):
        date = pd.to_datetime(date)
        return pd.to_datetime(self._date.loc[self._date['date'].shift(1) == date, 'date'].values[0])

    # 根据交易日找前一个交易日
    def get_last_trading_date(self, date):
        date = pd.to_datetime(date)
        return pd.to_datetime(self._date.loc[self._date['date'].shift(-1) == date, 'date'].values[0])

    # 是否是本月第一个交易日
    def if_first_trading_date(self, date):
        if not self.tradable_date(date):
            return False
        else:
            last_trading_date = self.get_last_trading_date(date)
            if date.month != last_trading_date.month:
                return True
            else:
                return False

    # 找某个月第一个交易日
    def get_monthly_first_trading_date(self, month):
        """

        :param month: '2019-01'
        :return:
        """
        now_earth_date = pd.to_datetime(month + '-01')
        while not self.tradable_date(now_earth_date):
            now_earth_date += timedelta(days=1)
        return now_earth_date.strftime('%Y-%m-%d')


if __name__ == '__main__':
    trade_calender = TradeCalender()
    dt = trade_calender.get_next_trading_date('2020-12-01')
    print(dt)
