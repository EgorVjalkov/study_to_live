import datetime

import pandas as pd

from database.mirror import Mirror


class TestMirror(Mirror):
    def __init__(self):
        super().__init__()
        self.date_of_last_update = datetime.datetime.now().minute

    @property
    def date(self):
        return self.date_of_last_update

    @date.setter
    def date(self, date: datetime):
        self.date_of_last_update = date

    def init_series(self) -> object:
        self.series = pd.Series({self.date: 'empty'}, name='STATUS')
        return self

    def update_by_date(self, date: datetime = None) -> object:
        #last = self.series.index[-1]
        self.date = date
        print(self.date)
        self.series = pd.concat([self.series,
                                 pd.Series({self.date: 'empty'})])
        return self

if __name__ == '__main__':

    tm = TestMirror()
    tm.init_series()
    print(tm.series)
    tm.update_by_date()
    print(tm.series)
    tm.update_by_date()
    print(tm.series)
    tm.update_by_date()
    print(tm.series)
