import datetime
import pandas as pd
import os
from pathlib import Path
from path_maker import PathMaker
from temp_db.unfilled_rows_db import MonthDB
from filler.date_funcs import yesterday, today, week_before_, last_date_of_past_month, get_dates_dict
from filler.day_row import DayRow


class Mirror:
    def __init__(self, path_maker: PathMaker,
                 ser: pd.Series = pd.Series()):
        self.series = ser
        self.path_to = path_maker
        self.path_to_db = self.path_to.temp_db
        self.date_of_last_update = None

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

    def temp_db_exists(self, path):
        return path in self.months_db_paths

    def init_(self, from_: str) -> object:
        series_list = []
        t = today()
        wbd = week_before_(t)
        if wbd.month == t.month:
            day_list = [t]
        else:
            day_list = [last_date_of_past_month(t), t]

        for day in day_list:
            temp_db = MonthDB(self.path_to.months_temp_db_by(day),
                              self.path_to.mother_frame_by(day))

            if not self.temp_db_exists(temp_db.path_to_temp_db):  # <- сщздаем пустую базу
                temp_db.create_empty_temp_db(temp_db.mf_from_file.columns.to_list())

            db_frame = temp_db.get_actual_dayrows_df_(from_, by_date=day)
            if not db_frame.empty:
                series_list.append(db_frame['STATUS'])
        self.init_series_and_last_date(series_list)
        return self

    def init_series_and_last_date(self, series_list: list) -> object:
        if len(series_list) > 1:
            self.series = pd.concat(series_list)
        else:
            self.series = series_list[0]
        self.series = self.series.sort_index()
        self.date_of_last_update = today()
        return self

    @property
    def need_update(self):
        flag = self.date_of_last_update < today()
        return flag

    def update_by_date(self) -> object:
        t = today()
        delta = t - self.date_of_last_update
        for day in range(1, delta.days+1):
            date = self.date_of_last_update + datetime.timedelta(days=day)
            done = 'empty'
            self.series = pd.concat(
                [self.series,
                 pd.Series({date: done})]).sort_index()
        self.date_of_last_update = t
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

    def get_paths_by(self, date: datetime.date) -> tuple:
        return (self.path_to.months_temp_db_by(date),
                self.path_to.mother_frame_by(date))

    def get_days_for_coef_correction(self) -> pd.Series:
        series_list = []
        t = today()
        day_dict = get_dates_dict(t, 7, 7)

        for day in day_dict:
            mdb = MonthDB(self.path_to.months_temp_db_by(day_dict[day]),
                          self.path_to.mother_frame_by(day_dict[day]))
            mf = mdb.mf_from_file
            if day == 's':
                days_status = mf[mf.index >= day_dict[day]]['STATUS']
            else:
                days_status = mf[mf.index <= day_dict[day]]['STATUS']

            if self.temp_db_exists(mdb.path_to_temp_db):
                status_from_temp = mdb.temp_db_from_file['STATUS']
                for date in days_status.index:
                    if date in status_from_temp.index:
                        days_status.loc[date] = status_from_temp.loc[date]

            series_list.append(days_status)

        self.init_series_and_last_date(series_list)

        return self.series

    def save_day_data(self, day: DayRow) -> object:
        paths = self.get_paths_by(day.date)
        temp_db = MonthDB(*paths)
        if day.is_filled or day.is_empty:
            data_type = 'mf'
            if day.is_filled:
                temp_db.del_filled_row(day.date)
                self.series = self.series[self.series.index != day.date]  # <- рескан серии после удаления
        else:
            data_type = 'temp_db'
            self.series.at[day.date] = day.mark

        print(f'SAVE: {day.mark} --> {data_type}')
        frame = temp_db.load_as_(data_type)
        frame.loc[day.date] = day.row
        temp_db.save_(frame, as_=data_type, mode='a')
        return self

    def load_prices_by(self, date: datetime.date, for_: str):
        path = self.path_to.mother_frame_by(date)
        sheet_name = for_ if for_ == 'coefs' else 'price'
        return pd.read_excel(path, sheet_name=sheet_name, index_col=0)
