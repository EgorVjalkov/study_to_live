import datetime
import pandas as pd
import os
from pathlib import Path
from path_maker import PathMaker
from row_db.unfilled_rows_db import UnfilledRowsDB
from date_constants import yesterday, today, week_before_day


class Mirror:
    def __init__(self, path_maker: PathMaker,
                 ser: pd.Series = pd.Series()):
        self.series = ser
        self.path_to = path_maker
        self.path_to_db = self.path_to.temp_db

    @property
    def no_dbs(self):
        return self.months_db_paths == []

    def init_temp_dbs(self):
        print('init')
        for day in [week_before_day, today]:
            print(day)
            path = self.path_to.mother_frame_by(day)
            mother_frame = self.load_('mf', by_path=path)
            temp_db = UnfilledRowsDB(self.path_to.months_temp_db_by(day))
            temp_db.replace_temp_db(mother_frame)
            temp_db.save_temp_db()

    @property
    def need_scan(self):
        return self.series.empty

    @property
    def months_db_paths(self) -> list:
        files = os.listdir(self.path_to_db)
        if files:
            return [Path(self.path_to_db, file_name) for file_name in files]
        return files

    def update_after_scan(self):
        series_list = []
        for path in self.months_db_paths:
            db_frame = self.load_('temp_db', by_path=path)
            series_list.append(db_frame['DONE'])
        if len(series_list) > 1:
            self.series = pd.concat(series_list)
        else:
            self.series = series_list[0]
        self.series = self.series.sort_index()
        return self.series

    def update_by_date(self):
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

    def load_(self,
              data: str,
              by_date=None,
              by_path=None,
              from_: str = '') -> pd.DataFrame:

        if by_path:
            path = by_path
        else:
            if data in 'mf' or from_ == 'mf':
                path = self.path_to.mother_frame_by(by_date)
            else:
                path = self.path_to.months_temp_db_by(by_date)

        frame_: pd.DataFrame = pd.read_excel(path, sheet_name='vedomost')
        frame_['DATE'] = frame_['DATE'].map(lambda _date: _date.date())
        frame_ = frame_.set_index('DATE')

        if data == 'row':
            return frame_.loc[by_date]
        else:
            return frame_


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


