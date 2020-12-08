from datetime import timedelta


class EarthCalender:
    def __init__(self, begin_date, end_date):
        self.begin_date = begin_date
        self.end_date = end_date
        self.now_date = begin_date

    def last_date(self):
        return self.now_date - timedelta(days=1)

    def next_date(self):
        return self.now_date + timedelta(days=1)

    def next_day(self):
        self.now_date += timedelta(days=1)
