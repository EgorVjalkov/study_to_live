import datetime
import pandas as pd
import os
from pathlib import Path


def convert_date_for_path(date: datetime.date):
    return date.strftime("%d_%m_%y")


def convert_date_from(file_name: str) -> str:
    name = file_name.split('.')[0]
    date_part = name.split('(')[0]
    return date_part.replace('_', '.')
# ссделал класс дайроу нужно продолжать


class DayRow:
    def __init__(self,
                 day_row: pd.DataFrame = pd.DataFrame(),
                 path: str = ''):

        self.day_row: pd.DataFrame = day_row
        self.path_to: str = path

    @property
    def day_index(self) -> int:
        return self.day_row.index[0]

    @property
    def categories(self) -> pd.Series:
        cf: pd.DataFrame = self.day_row[[i for i in self.day_row.columns if i.find(':') == 1]]
        return cf.loc[self.day_index]

    @property
    def accessories(self) -> pd.Series:
        cf: pd.DataFrame = self.day_row[[i for i in self.day_row.columns if not i.find(':') == 1]]
        return cf.loc[self.day_index]

    @property
    def mark(self):
        return self.day_row.at[self.day_index, 'DONE']

    @property
    def is_mark_filled(self) -> bool:
        return pd.notna(self.mark)

    @property
    def date(self) -> datetime.date:
        return self.day_row.at[self.day_index, 'DATE']

    def load_day_row(self):
        self.day_row = pd.read_excel(self.path_to)
        return self.day_row

    def create_row(self, path_to_file):
        with pd.ExcelWriter(
                path_to_file,
                mode='w'
        ) as writer:
            self.day_row.to_excel(writer)


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

    def contains(self, date) -> bool:
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
            path_to_file = Path(self.path_to_db, f'{convert_date_for_path(row.date)}.xlsx')
        row.create_row(path_to_file)

    def load_rows_dict_for(self, recipient) -> dict:
        done_mark = recipient[0]
        files_list = [f_name for f_name in self.temp_files
                      if done_mark not in f_name]
        for f_name in files_list:
            f_path = Path(self.path_to_db, f'{f_name}')
            f_name_for_tg = convert_date_from(f_name)
            self.db[f_name_for_tg] = f_path
        return self.db
