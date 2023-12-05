import datetime
import pandas as pd
import os
from pathlib import Path
from day_row import DayRow
from path_maker import PathMaker


today: datetime.date = datetime.date.today()
yesterday: datetime.date = today - datetime.timedelta(days=1)


class Converter:
    def __init__(self,
                 file_name: str = '',
                 date_in_str: str = '',
                 date_object: datetime.date = datetime.date.today()
                 ):
        self.f_name = file_name
        self.date_in_str = date_in_str
        self.date_object = date_object

        self.to_conversion = None

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


class Mirror:
    def __init__(self, path_maker: PathMaker,
                 ser: pd.Series = pd.Series()):
        self.series = ser
        self.path_to = path_maker
        self.path_to_db = self.path_to.temp_db

    @property
    def need_scan(self):
        return self.series.empty

    @property
    def months_db_paths(self) -> list:
        files = os.listdir(self.path_to_db)
        return [Path(self.path_to_db, file_name) for file_name in files]

    def update_after_scan(self):
        series_list = []
        for path in self.months_db_paths:
            db_frame = self.load_('temp_db', by_path=path)
            series_list.append(db_frame['DONE'])
        if len(series_list) > 1:
            self.series = pd.concat(series_list)
        else:
            self.series = series_list[0]
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
            if data == 'mf' or from_ == 'mf':
                path = self.path_to.vedomost_by(by_date)
            else:
                path = self.path_to.months_temp_db_by(by_date)

        frame_: pd.DataFrame = pd.read_excel(path, sheet_name='vedomost')
        frame_['DATE'] = frame_['DATE'].map(lambda _date: _date.date())
        frame_ = frame_.set_index('DATE')
        print(frame_)

        if data == 'row':
            return frame_.loc[by_date]
        else:
            return frame_


class UnfilledRowsDB:
    def __init__(self):
        self.mirror = None

    def __repr__(self):
        s_for_print: pd.Series = self.mirror_frame.set_index('date_from_tg')['DONE']
        list_ = [f'{i}: {s_for_print[i]}' for i in s_for_print.index]
        return f'DB({", ".join(list_)})'

    @property
    def mirror_frame(self) -> pd.DataFrame:
        self.mirror = pd.DataFrame()
        dbs = []
        if self.months_db_paths:
            for p in self.months_db_paths:
                dbs.append(self.get_frame(p))
            self.mirror: pd.DataFrame = Mirror().update(dbs)
        return self.mirror

    def contains(self, path_to_db):
        return path_to_db in self.months_db_paths

    @staticmethod
    def mf_is_newer_than_db(path_to_mf: Path, path_to_db: Path) -> bool:
        date_temp_db = os.path.getmtime(path_to_db)
        date_mf_db = os.path.getmtime(path_to_mf)
        return date_mf_db > date_temp_db # <- материнский новее

    @staticmethod
    def update_temp_db(mother_frame: pd.DataFrame,
                       temp_db: pd.DataFrame) -> pd.DataFrame:
        date_filter = mother_frame['DATE'].map(lambda date_: date_ in (yesterday, today))
        update_from_mf = mother_frame[date_filter == True]
        for i in update_from_mf.index:
            if i not in temp_db.index:
                temp_db.loc[i] = update_from_mf.loc[i]
        return temp_db

    @staticmethod
    def replace_temp_db(mother_frame: pd.DataFrame) -> pd.DataFrame:
        unfilled_rows: pd.DataFrame = mother_frame[mother_frame['DATE'] <= today]
        unfilled_rows: pd.DataFrame = unfilled_rows[unfilled_rows['DONE'] != 'Y']
        db_from_mf = unfilled_rows
        if yesterday not in db_from_mf['DATE'].values:
            yesterday_row: pd.DataFrame = mother_frame[mother_frame['DATE'] == yesterday]
            db_from_mf = pd.concat([yesterday_row, db_from_mf]).sort_index()
        return db_from_mf

    @staticmethod
    def save_temp_db(path: Path, temp_db: pd.DataFrame):
        with pd.ExcelWriter(path=path,
                            mode='w',
                            engine='openpyxl',
                            ) as writer:
            temp_db.to_excel(writer, index=True)

    # есть мыслишка, что надо в зеркале оставлять ссылку на материнский фрейм. и если в бд их заявлено 2, сверять с обоими
    # и уже потом поступать как надо

    def update(self):
        dbs = {}
        if not self.contains(PathMaker(today).to_months_temp_db):
            mf = self.get_frame(path=PathMaker(today).to_vedomost, sheet_name='vedomost')
            dbs[PathMaker().to_months_temp_db] = self.replace_temp_db(mf)

        mirror: pd.DataFrame = self.mirror_frame
        paths: pd.DataFrame = mirror.get(['path_to_mf', 'path_to_db']).drop_duplicates()
        print(paths)
        for row in paths.index:
            # замуть с индексацией
            paths = paths.loc[row]
            print(paths)
            path_to_mf, path_to_db = paths[0], paths[1]
            mf = self.get_frame(path=path_to_mf, sheet_name='vedomost')
            if (not self.contains(path_to_db) |
                    self.mf_is_newer_than_db(path_to_db, path_to_mf)):
                dbs[path_to_db] = self.replace_temp_db(mf)
            else:
                temp_db = self.get_frame(path_to_db)
                dbs[path_to_db] = self.update_temp_db(mf, temp_db)

        for path in dbs:
            self.save_temp_db(path, dbs[path])

        #mother_frame = self.mother_frame
        #print(self.mother_frame)
        #self.save_temp_db(temp_db)

    def create_row(self, row: DayRow) -> DayRow:
        if self.contains(row.date):
            full_path: Path = self.get_full_path(row.date)
            print(full_path)
            if full_path in self.empty_rows_paths:
                os.remove(full_path)
            else:
                existed_row: DayRow = DayRow(path=full_path).load_day_row()
                print(f'existed {existed_row}')
                row.concat_row_with(existed_row)

        if row.is_mark_filled:
            path_to_file = Path(self.path_to_db, f'{date_part}({row.mark}).xlsx')
        else:
            if row.is_empty:
                path_to_file = Path(self.path_to_db, f'{date_part}(empty).xlsx')
            else:
                path_to_file = Path(self.path_to_db, f'{date_part}.xlsx')
        row.create_row(path_to_file)
