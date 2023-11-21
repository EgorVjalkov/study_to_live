import datetime
import pandas as pd
import os


def convert_date(date: datetime.date):
    return date.strftime("%d_%m_%y")
# ссделал класс дайроу нужно продолжать
# что перкое при инициации? создпине или проверка на налицие


class DayRow:
    def __init__(self, day_row: pd.DataFrame, path: str = ''):
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
        self.day_row = None
        self.day_index = None

    def contains(self, date) -> bool:
        flag: bool = False
        files_list = [n for n in os.listdir(self.path_to_db) if convert_date(date) in n]
        if files_list:
            flag: bool = True
        return flag

    def create_rows(self, mother_frame: pd.DataFrame):
        day_rows: pd.DataFrame = mother_frame[mother_frame['DATE'] <= self.date]
        day_rows: pd.DataFrame = day_rows[day_rows['DONE'] != 'Y']
        for index in day_rows.index:
            row = DayRow(day_row=mother_frame[index:index+1])
            if row.is_mark_filled:
                path_to_file = f'{self.path_to_db}/{convert_date(row.date)}_{row.mark}.xlsx'
            else:
                path_to_file = f'{self.path_to_db}/{convert_date(row.date)}.xlsx'
            row.create_row(path_to_file)
