from datetime import timedelta
import pandas as pd


class EarthCalender:
    def __init__(self, begin_date, end_date):
        self.begin_date = pd.to_datetime(begin_date)
        self.end_date = pd.to_datetime(end_date)
        self.now_date = pd.to_datetime(begin_date)

    def last_date(self):
        return self.now_date - timedelta(days=1)

    def next_date(self):
        return self.now_date + timedelta(days=1)

    def next_day(self):
        self.now_date += timedelta(days=1)

    def end_of_test(self):
        if self.now_date <= self.end_date:
            return False
        else:
            return True