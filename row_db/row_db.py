import datetime
from datetime import date
import pandas as pd
import os
from pathlib import Path
from day_row import DayRow


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


class DayRowsDB:
    def __init__(self, path_to: str):
        self.date: datetime.date = datetime.date.today()
        self.path_to_db = path_to
        self.db = {}

    @property
    def yesterday(self):
        return self.date - datetime.timedelta(days=1)

    @property
    def temp_files(self) -> list:
        return os.listdir(self.path_to_db)

    @property
    def temp_files_paths_dict(self) -> dict:
        return {f_name: Path(self.path_to_db, f_name) for f_name in self.temp_files}

    def get_full_path(self, date_object: datetime.date) -> Path | None:
        path_part = Converter(date_object=date_object).to('path')
        path_in_list = [f_name for f_name in self.temp_files_paths_dict
                        if path_part in f_name]
        assert len(path_in_list) <= 1, 'несколько файлов'
        return path_in_list[0] if path_in_list else None

    def clear_except(self, important_paths: pd.Series):
        for path in self.temp_files_paths_dict:
            if path not in important_paths.values:
                os.remove(path)

    def write_filled_to_mf_and_del(self, mother_frame: pd.DataFrame, path_to_mf: Path):
        for f_name in self.temp_files_paths_dict:
            if 'Y' in f_name:
                filled_row: DayRow = DayRow(path=self.temp_files_paths_dict[f_name]).load_day_row()
                mother_frame.loc[filled_row.i] = filled_row.day_row
                os.remove(self.temp_files_paths_dict[f_name])

        with pd.ExcelWriter(path=path_to_mf,
                            mode='a',
                            engine='openpyxl',
                            if_sheet_exists='replace'
                            ) as mf_writer:
            mother_frame.to_excel(mf_writer, sheet_name='vedomost', index=False)

    def update(self, mother_frame: pd.DataFrame, path_to_mf: Path):
        unfilled_rows: pd.DataFrame = mother_frame[mother_frame['DATE'] <= self.date]
        unfilled_rows: pd.DataFrame = unfilled_rows[unfilled_rows['DONE'] != 'Y']
        important_dates: pd.Series = unfilled_rows['DATE']
        if self.yesterday not in important_dates.values:
            yesterday_ser: pd.Series = mother_frame[mother_frame['DATE'] == self.yesterday]['DATE']
            important_dates = pd.concat([important_dates, yesterday_ser])
        important_paths = important_dates.map(self.get_full_path)
        self.clear_except(important_paths)
        self.write_filled_to_mf_and_del(mother_frame, path_to_mf)
        for i in important_paths.index:
            path_ = important_paths[i]
            print(path_)
            if not path_:
                self.create_row(mother_frame[i:i+1])

    def create_row(self, row: pd.DataFrame):
        row = DayRow(day_row=row)
        date_part = Converter(date_object=row.date).to('path')
        if row.is_mark_filled:
            path_to_file = Path(self.path_to_db, f'{date_part}({row.mark}).xlsx')
        else:
            if row.is_empty:
                path_to_file = Path(self.path_to_db, f'{date_part}(empty).xlsx')
            else:
                path_to_file = Path(self.path_to_db, f'{date_part}.xlsx')
        row.create_row(path_to_file)

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
