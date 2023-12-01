import datetime
import pandas as pd
import os
from pathlib import Path
from day_row import DayRow


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
    def __init__(self):
        self.frame = pd.DataFrame

    def __repr__(self):
        for_print = [f'{i}: {self.frame.at[i]}'
                     for i in self.frame.index]
        return f'MirrorDB({", ".join(for_print)})'

    def update(self, db: pd.DataFrame):
        self.frame = db.get(['DATE', 'DONE'])
        self.frame['date_from_tg'] = self.frame['DATE'].map(
            lambda date_: Converter(date_object=date_).to('str'))
        return self.frame


class UnfilledRowsDB:
    def __init__(self, path_to_db: Path, path_to_mf: Path):
        self.mirror_frame: pd.Series = pd.Series()
        self.path_to_db = path_to_db
        self.path_to_mf = path_to_mf

    def __repr__(self):
        for_print = [f'{i}: {self.mirror_frame.at[i]}'
                     for i in self.mirror_frame.index]
        return f'DB({", ".join(for_print)})'

    #def __call__(self, *args, **kwargs):
    #    self.mirror = Mirror().update(self.db)

    @property
    def exists(self):
        return os.path.isfile(self.path_to_db)

    @property
    def db(self) -> pd.DataFrame:
        db = pd.read_excel(self.path_to_db, index_col=0)
        db['DATE'] = db['DATE'].map(lambda date_: date_.date())
        return db

    @property
    def mother_frame(self) -> pd.DataFrame:
        mf: pd.DataFrame = pd.read_excel(self.path_to_mf, sheet_name='vedomost')
        mf['DATE'] = mf['DATE'].map(lambda date_: date_.date())
        return mf

    @property
    def is_newer_than_mf(self) -> bool:
        date_temp_db = os.path.getmtime(self.path_to_db)
        date_mf_db = os.path.getmtime(self.path_to_mf)
        return date_temp_db > date_mf_db # <- временный новее

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

    def save_temp_db(self, temp_db: pd.DataFrame):
        with pd.ExcelWriter(path=self.path_to_db,
                            mode='w',
                            engine='openpyxl',
                            ) as writer:
            temp_db.to_excel(writer)

    def update(self):
        mother_frame = self.mother_frame
        if not self.exists or not self.is_newer_than_mf:
            temp_db = self.replace_temp_db(mother_frame)
        else:
            temp_db = self.update_temp_db(mother_frame, self.db)
        self.mirror_frame = Mirror().update(temp_db)
        self.save_temp_db(temp_db)

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

    def load_rows_for(self, recipient: str, by_behavior: str) -> pd.Series:
        if by_behavior == 'for filling':
            r_done_mark = recipient[0]
            days_frame: pd.DataFrame = self.mirror_frame[self.mirror_frame['DONE'] != r_done_mark]
        elif by_behavior == 'for correction':
            days_frame: pd.DataFrame = self.mirror_frame[self.mirror_frame['DONE'] != 'empty']
            days_frame: pd.DataFrame = days_frame[days_frame['DATE'] >= yesterday]
        else:
            days_frame: pd.DataFrame = self.mirror_frame[self.mirror_frame['DATE'] == today]
        days_frame['row_index'] = days_frame.index
        return days_frame.set_index('date_from_tg')['row_index']
