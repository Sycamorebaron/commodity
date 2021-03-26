import pandas as pd


class Recorder:
    def __init__(self):
        self._equity_curve = []
        self._trade_hist = []

    def record_trade(self, info):
        for trade in info:
            self._trade_hist.append(trade)

    def record_equity(self, info):
        self._equity_curve.append(info)

    def trade_hist(self):
        return pd.DataFrame(self._trade_hist)

    def equity_curve(self):
        return pd.DataFrame(self._equity_curve)
