import datetime
import pandas as pd
import os
from pathlib import Path
from path_maker import PathMaker
from row_db.unfilled_rows_db import UnfilledRowsDB
from date_constants import yesterday, today, week_before_day
from day_row import DayRow


class Mirror:
    def __init__(self, path_maker: PathMaker,
                 ser: pd.Series = pd.Series()):
        self.series = ser
        self.path_to = path_maker
        self.path_to_db = self.path_to.temp_db
        self.last_date = today

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
            print(day)
            path = self.path_to.mother_frame_by(day)
            mother_frame = self.load_as_('mf', by_path=path)
            temp_db = UnfilledRowsDB(self.path_to.months_temp_db_by(day))
            db_frame = temp_db.replace_temp_db(mother_frame)
            series_list.append(db_frame['DONE'])
            temp_db.save_temp_db()
        self.update(series_list)

    @property
    def need_update(self):
        return self.last_date < today

    @property
    def months_db_paths(self) -> list:
        files = os.listdir(self.path_to_db)
        if files:
            return [Path(self.path_to_db, file_name) for file_name in files]
        return files

    def update(self, series_list=None):
        if not series_list:
            series_list = []
            for path in self.months_db_paths:
                db_frame = self.load_as_('temp_db', by_path=path)
                series_list.append(db_frame['DONE'])
        if len(series_list) > 1:
            self.series = pd.concat(series_list)
        else:
            self.series = series_list[0]
        self.series = self.series.sort_index()
        return self.series

    def update_by_date(self):
        # здесь похоже даже к серии нет нуждф обращаться, т.к. ластдейт итак один, нужно только его обновлять, да?
        self.last_date = today
        last_date = max(self.series.index.to_list())
        delta = today - last_date
        for day in range(1, delta.days+1):
            date = last_date + datetime.timedelta(days=day)
            done = 'empty'
            self.series = pd.concat(
                [self.series,
                 pd.Series({date: done})]).sort_index()

    def get_dates_for(self, recipient: str, by_behavior: str) -> pd.Series:
        if by_behavior == 'for filling':
            r_done_mark = recipient[0]
            days_ser: pd.Series = self.series[self.series != r_done_mark]
        elif by_behavior == 'for correction':
            days_ser: pd.Series = self.series[self.series != 'empty']
            days_ser: pd.Series = days_ser[days_ser.index >= yesterday]
        else:
            days_ser: pd.Series = self.series[self.series.index == today]
        return days_ser

    def get_path_to_(self,
                     data_type: str,
                     by_date=None,
                     by_path=None,
                     from_: str = '') -> Path:
        if by_path:
            path = by_path
        else:
            if data_type in 'mf' or from_ == 'mf':
                path = self.path_to.mother_frame_by(by_date)
            else:
                path = self.path_to.months_temp_db_by(by_date)
        return path

    def load_as_(self,
                 data_type: str,
                 by_date=None,
                 by_path=None,
                 from_: str = '') -> pd.DataFrame:
        path = self.get_path_to_(data_type, by_date, by_path, from_)
        frame_: pd.DataFrame = pd.read_excel(path, sheet_name='vedomost')
        frame_['DATE'] = frame_['DATE'].map(lambda _date: _date.date())
        frame_ = frame_.set_index('DATE')
        if data_type == 'row':
            return frame_.loc[by_date]
        else:
            return frame_

    def write_as_(self,
                  data_type: str,
                  df: pd.DataFrame,
                  by_date: datetime.date):
        path = self.get_path_to_(data_type, by_date)
        with pd.ExcelWriter(
                path,
                mode='a',
                engine='openpyxl',
                if_sheet_exists='replace'
        ) as writer:
            df.to_excel(writer, sheet_name='vedomost', index=True)

    def del_filled_row(self, day_date: datetime.date) -> object:
        temp_frame = self.load_as_('temp_db', by_date=day_date)
        temp_frame = temp_frame[temp_frame.index != day_date]
        self.write_as_('temp_db', temp_frame, day_date)
        self.series = self.series.index != day_date  # <- рескан серии
        return self

    def save_day_data(self, day_data: DayRow):
        if day_data.is_filled:
            data_type = 'mf'
            self.del_filled_row(day_data.date)
        else:
            data_type = 'temp_db'
            self.series.at[day_data.date] = day_data.mark
        frame = self.load_as_(data_type, by_date=day_data.date)
        frame.loc[day_data.date] = day_data.row
        self.write_as_(data_type, frame, day_data.date)


class Converter:
    def __init__(self,
                 file_name=None,
                 date_in_str=None,
                 date_object=None
                 ):
        self.f_name = file_name
        self.date_in_str = date_in_str
        self.date_object = date_object

    @property
    def splitted_f_name(self) -> dict:
        parts = self.f_name.split('(')
        if len(parts) < 2:
            date_in_str = parts[0].replace('.xlsx', '')
            mark = ''
        else:
            date_in_str, mark = parts[0], parts[1].replace(').xlsx', '')
        return {'date': date_in_str,
                'mark': mark}

    @property
    def mark(self) -> str:
        return self.splitted_f_name['mark']

    @property
    def date_from_f_name(self) -> str:
        return self.splitted_f_name['date']

    @property
    def standard_date(self):
        if self.f_name:
            return self.date_from_f_name.replace('_', '.')
        if self.date_in_str:
            return self.date_in_str
        if self.date_object:
            return self.date_object.strftime("%d.%m.%y")

    def to(self, mode):
        if mode == 'date_object':
            date_ = datetime.datetime.strptime(self.standard_date, '%d.%m.%y')
            date_ = date_.date()
            return date_
        if mode == 'path':
            return self.standard_date.replace('.', '_')
        if mode == 'str':
            return self.standard_date


#a = Converter(file_name='21_11_23(empty).xlsx')
#print(a.splitted_f_name)
#a = Converter(file_name='21_11_23.xlsx')
#print(a.splitted_f_name)
#a = Converter(file_name='21_11_23(empty).xlsx').to('str')
#print(a)
#a = Converter(date_object=datetime.date.today()).to('str')
#print(a)
#a = Converter(date_object=datetime.date.today()).to('path')
#print(a)


