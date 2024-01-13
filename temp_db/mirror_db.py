import datetime
import pandas as pd
import os
from pathlib import Path
from path_maker import PathMaker
from temp_db.unfilled_rows_db import MonthDB
from filler.date_funcs import yesterday, today, week_before_
from filler.day_row import DayRow


class Mirror:
    def __init__(self, path_maker: PathMaker,
                 ser: pd.Series = pd.Series()):
        self.series = ser
        self.path_to = path_maker
        self.path_to_db = self.path_to.temp_db
        self.last_date = None

    def __repr__(self):
        if self.series.empty:
            return 'Mirror(empty)'
        else:
            return (f'Mirror:'
                    f'{self.series}')

    @property
    def dbs_files_list(self):
        return os.listdir(self.path_to_db)

    @property
    def months_db_paths(self) -> list:
        return [Path(self.path_to_db, file_name) for file_name in self.dbs_files_list]

    @property
    def no_dbs(self):
        return self.dbs_files_list == []

    def init_(self, from_: str) -> object:
        series_list = []
        t = today()
        wbd = week_before_(t)
        if wbd.month == t.month:
            day_list = [t]
        else:
            day_list = [wbd, t]

        for day in day_list:
            temp_db = MonthDB(self.path_to.months_temp_db_by(day),
                              self.path_to.mother_frame_by(day))
            db_frame = temp_db.get_actual_dayrows_df_(from_, by_date=day)
            if not db_frame.empty:
                # здесь нужео создать пустую базу
                series_list.append(db_frame['STATUS'])
                temp_db.save_(db_frame, as_='temp_db', mode='w') # не сохраняем
        self.init_series_and_last_date(series_list)
        return self

    def init_series_and_last_date(self, series_list: list) -> object:
        if len(series_list) > 1:
            self.series = pd.concat(series_list)
        else:
            self.series = series_list[0]
        self.series = self.series.sort_index()
        self.last_date = self.series.index.to_list()[-1]
        print(self.series)
        return self

    @property
    def need_update(self):
        flag = self.last_date < today()
        return flag

    def update_by_date(self) -> object:
        delta = today() - self.last_date
        for day in range(1, delta.days+1):
            date = self.last_date + datetime.timedelta(days=day)
            done = 'empty'
            self.series = pd.concat(
                [self.series,
                 pd.Series({date: done})]).sort_index()
        print(self.series)
        return self

    def get_dates_for(self, recipient: str, by_behavior: str) -> pd.Series:
        if by_behavior == 'filling':
            r_done_mark = recipient[0]
            days_ser: pd.Series = self.series[self.series != r_done_mark]
        elif by_behavior == 'correction':
            yesterday_ = yesterday()
            days_ser: pd.Series = self.series[self.series.index >= yesterday_]
            if yesterday_ not in days_ser.index:
                yesterday_ser = pd.Series({yesterday_: 'Y'})
                days_ser = pd.concat([yesterday_ser, days_ser]).sort_index()
            days_ser: pd.Series = days_ser[days_ser != 'empty']
        else:
            days_ser: pd.Series = self.series[self.series.index == today()]

        print(f'get_dates_for_{recipient}_by_{by_behavior}')
        print(days_ser)

        return days_ser

    def get_paths_by(self, date: datetime.date = today) -> tuple:
        return (self.path_to.months_temp_db_by(date),
                self.path_to.mother_frame_by(date))

    def save_day_data(self, day: DayRow) -> object:
        paths = self.get_paths_by(day.date)
        temp_db = MonthDB(*paths)
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

    def load_prices_by(self, date: datetime.date, for_: str):
        path = self.path_to.mother_frame_by(date)
        sheet_name = for_ if for_ == 'coefs' else 'price'
        return pd.read_excel(path, sheet_name=sheet_name, index_col=0)
