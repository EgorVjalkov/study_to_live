import datetime
from datetime import date
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


class MirrorDB:
    def __init__(self):
        self.db_mirror = pd.Series()

    def __repr__(self):
        for_print = [f'{i}: {self.db_mirror.at[i]}'
                     for i in self.db_mirror.index]
        return f'MirrorDB({", ".join(for_print)})'

    def update(self, db: pd.DataFrame):
        self.db_mirror = db.get(['DATE', 'DONE']).set_index('DATE')['DONE']
        return self.db_mirror


class UnfilledRowsDB:
    def __init__(self, path_to_db: Path, path_to_mf: Path):
        self.mirror: pd.Series = pd.Series()
        self.path_to_db = path_to_db
        self.path_to_mf = path_to_mf

    def __repr__(self):
        for_print = [f'{i}: {self.mirror.at[i]}'
                     for i in self.mirror.index]
        return f'DB({", ".join(for_print)})'

    def __call__(self, *args, **kwargs):
        self.mirror = MirrorDB().update(self.db)

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

    @property
    def days_tg_format(self) -> list:
        return [Converter(date_object=date_).to('str')
                for date_ in self.mirror.index]

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
            #temp_db = self.db
            #temp_db = self.update_temp_db(mother_frame, temp_db)
            temp_db = self.update_temp_db(mother_frame, self.db)
        self.mirror = MirrorDB().update(temp_db)
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

    def concat_rows(self):
        pass

    def load_rows_dict_for(self, recipient: str, behavior: str) -> dict:
        if behavior == 'for filling':
            done_mark = recipient[0]
            files_list = [f_name for f_name in self.temp_files_paths_dict
                          if done_mark not in f_name]
        elif behavior == 'for correction':
            files_list = [f_name for f_name in self.temp_files_paths_dict
                          if 'empty' not in f_name]
            if files_list:
                files_list = [f_name for f_name in files_list
                              if Converter(file_name=f_name).to('date') >= self.yesterday]
        else:
            files_list = [f_name for f_name in self.temp_files_paths_dict
                          if Converter(file_name=f_name).to('date') == self.date]

        for f_name in files_list:
            f_path = Path(self.path_to_db, f'{f_name}')
            f_name_for_tg = Converter(file_name=f_name).to('str')
            self.db[f_name_for_tg] = f_path
        return self.db
