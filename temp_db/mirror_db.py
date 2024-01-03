import datetime
import pandas as pd
import os
from pathlib import Path
from path_maker import PathMaker
from temp_db.unfilled_rows_db import UnfilledRowsDB
from filler.date_constants import yesterday, today, week_before_day
from filler.day_row import DayRow


class Mirror:
    def __init__(self, path_maker: PathMaker,
                 ser: pd.Series = pd.Series()):
        self.series = ser
        self.path_to = path_maker
        self.path_to_db = self.path_to.temp_db
        self.last_date = today

    def __repr__(self):
        if self.series.empty:
            return 'Mirror(empty)'
        else:
            return (f'Mirror:'
                    f'{self.series}')

    @property
    def months_db_paths(self) -> list:
        files = os.listdir(self.path_to_db)
        if files:
            return [Path(self.path_to_db, file_name) for file_name in files]
        return files

    @property
    def no_dbs(self):
        return self.months_db_paths == []

    def init_temp_dbs(self):
        print('init')
        series_list = []
        if week_before_day.month == today.month:
            day_list = [today]
        else:
            day_list = [week_before_day, today]
        for day in day_list:
            temp_db = UnfilledRowsDB(self.path_to.months_temp_db_by(day),
                                     self.path_to.mother_frame_by(day))
            db_frame = temp_db.init_temp_db()
            if not db_frame.empty:
                series_list.append(db_frame['STATUS'])
                temp_db.save_(db_frame, as_='temp_db', mode='w')
        self.update_by_dbs(series_list)

    @property
    def need_update(self):
        return self.last_date < today

    def update_by_date(self):
        delta = today - self.last_date
        for day in range(1, delta.days+1):
            date = self.last_date + datetime.timedelta(days=day)
            done = 'empty'
            self.series = pd.concat(
                [self.series,
                 pd.Series({date: done})]).sort_index()
        self.last_date = today

    def update_by_dbs(self, series_list=None):
        if not series_list:
            series_list = []
            for path in self.months_db_paths:
                temp_db = UnfilledRowsDB(path).temp_db_from_file
                series_list.append(temp_db['STATUS'])
        if len(series_list) > 1:
            self.series = pd.concat(series_list)
        else:
            self.series = series_list[0]
        self.series = self.series.sort_index()
        return self.series

    def get_dates_for(self, recipient: str, by_behavior: str) -> pd.Series:
        if by_behavior == 'for filling':
            r_done_mark = recipient[0]
            days_ser: pd.Series = self.series[self.series != r_done_mark]
        elif by_behavior == 'for correction':
            days_ser: pd.Series = self.series[self.series != 'empty']
            days_ser: pd.Series = days_ser[days_ser.index >= yesterday]
            if yesterday not in days_ser.index:
                yesterday_ser = pd.Series({yesterday: 'Y'})
                days_ser = pd.concat([yesterday_ser, days_ser])
        else:
            days_ser: pd.Series = self.series[self.series.index == today]
        print(days_ser)
        return days_ser

    def get_paths_by(self, date: datetime.date = today) -> tuple:
        return (self.path_to.months_temp_db_by(date),
                self.path_to.mother_frame_by(date))

    def save_day_data(self, day: DayRow) -> object:
        paths = self.get_paths_by(day.date)
        temp_db = UnfilledRowsDB(*paths)
        if day.is_filled:
            data_type = 'mf'
            temp_db.del_filled_row(day.date)
            self.series = self.series[self.series.index != day.date]  # <- рескан серии
        else:
            data_type = 'temp_db'
            self.series.at[day.date] = day.mark

        print(f'{day.mark} --> {data_type}')
        frame = temp_db.load_as_(data_type)
        frame.loc[day.date] = day.row
        temp_db.save_(frame, as_=data_type, mode='a')
        return self

    def load_prices_by(self, date: datetime.date):
        path = self.path_to.mother_frame_by(date)
        return pd.read_excel(path, sheet_name='price', index_col=0)
