import datetime
from typing import Hashable
import pandas as pd


class DayRow:
    def __init__(self, day_row: pd.Series = pd.Series()):
        self.row = day_row

    def __repr__(self):
        return f'{self.date}({self.categories.to_dict()})'

    @property
    def categories(self) -> pd.Series:
        cat = self.row.index.map(lambda i: i.find(':') == 1)
        cat = self.row[cat == True]
        return cat

    @categories.setter
    def categories(self, categories_dict: dict):
        for cat in categories_dict:
            self.row.at[cat] = categories_dict[cat]

    @property
    def accessories(self) -> pd.Series:
        acc = self.row.index.map(lambda i: not i.find(':') == 1)
        acc = self.row[acc == True]
        return acc

    @property
    def filled_cells(self):
        filled_flag_ser = self.categories.map(pd.notna)
        filled = self.categories[filled_flag_ser == True]
        return filled

    @property
    def mark(self):
        return self.row.at['DONE']

    @mark.setter
    def mark(self, mark):
        self.row.at['DONE'] = mark

    @property
    def is_mark_filled(self) -> bool:
        return pd.notna(self.mark)

    @property
    def date(self) -> datetime.date:
        return self.row.name

    @property
    def need_common_filling(self):
        team_data = self.row.acc_frame.at[self.row.day_index, 'COM']
        flag = True if len(team_data.split(',')) < 1 else False
        return flag

    @property
    def is_empty(self) -> bool:
        return self.mark == 'empty'

    @property
    def is_filled(self) -> bool:
        nans = [i for i in self.row if pd.isna(i)]
        return nans == []
