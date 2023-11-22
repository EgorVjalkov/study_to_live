import datetime
import pandas as pd
import os
from pathlib import Path
from day_row import DayRow


def convert_date_for_path(date: datetime.date):
    return date.strftime("%d_%m_%y")


def convert_date_from(file_name: str, to: str = 'str') -> str:
    name = file_name.split('.')[0]
    date_part = name.split('(')[0]
    if to == 'date':
        date_ = datetime.datetime.strptime(date_part, '%d_%m_%y')
        date_ = date_.date()
    else:
        date_ = date_part.replace('_', '.')
    return date_


today = datetime.date.today()
date = convert_date_from(file_name='21_11_23', to='date')
print(today, date)


class DayRowsDB:
    def __init__(self, path_to: str):
        self.date: datetime.date = datetime.date.today()
        self.path_to_db = path_to
        self.db = {}

    @property
    def temp_files(self):
        return os.listdir(self.path_to_db)

    def update(self, mother_frame: pd.DataFrame):
        print(mother_frame['DATE'], self.date)
        unfilled_rows: pd.DataFrame = mother_frame[mother_frame['DATE'] <= self.date]
        unfilled_rows: pd.DataFrame = unfilled_rows[unfilled_rows['DONE'] != 'Y']
        for index in unfilled_rows.index:
            date = mother_frame.at[index, 'DATE']
            if not self.contains(date):
                self.create_row(mother_frame[index: index+1])

    def contains(self, date: datetime.date) -> bool:
        flag: bool = False
        files_list = [n for n in self.temp_files if convert_date_for_path(date) in n]
        if files_list:
            flag: bool = True
        return flag

    def create_row(self, row: pd.DataFrame):
        row = DayRow(day_row=row)
        if row.is_mark_filled:
            path_to_file = Path(self.path_to_db, f'{convert_date_for_path(row.date)}({row.mark}).xlsx')
        else:
            if row.is_empty:
                path_to_file = Path(self.path_to_db, f'{convert_date_for_path(row.date)}(empty).xlsx')
            else:
                path_to_file = Path(self.path_to_db, f'{convert_date_for_path(row.date)}.xlsx')
        row.create_row(path_to_file)

    def load_rows_dict_for(self, recipient: str, behavior: str) -> dict:
        if behavior == 'for filling':
            done_mark = recipient[0]
            files_list = [f_name for f_name in self.temp_files
                          if done_mark not in f_name]
        elif behavior == 'for correction':
            files_list = [f_name for f_name in self.temp_files
                          if 'empty' not in f_name]
            if files_list:
                yesterday = self.date - datetime.timedelta(days=1)
                files_list = [f_name for f_name in files_list
                              if convert_date_from(f_name, to='date') >= yesterday]
        else:
            files_list = [f_name for f_name in self.temp_files
                          if convert_date_from(f_name, to='date') == self.date]

        for f_name in files_list:
            f_path = Path(self.path_to_db, f'{f_name}')
            f_name_for_tg = convert_date_from(f_name)
            self.db[f_name_for_tg] = f_path
        return self.db
