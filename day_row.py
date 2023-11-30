import datetime
import pandas as pd
import numpy as np
from pathlib import Path


class DayRow:
    def __init__(self,
                 day_row: pd.DataFrame = pd.DataFrame(),
                 path: Path = ''):

        self.row: pd.DataFrame = day_row
        self.path_to: Path = path

    def __repr__(self):
        return f'DayRow({self.categories.to_dict()})'

    @property
    def i(self) -> int:
        return self.row.index[0]

    @property
    def categories(self) -> pd.Series:
        cf: pd.DataFrame = self.row[[i for i in self.row.columns if i.find(':') == 1]]
        return cf.loc[self.i]

    @categories.setter
    def categories(self, categories_dict: dict):
        for cat in categories_dict:
            self.row.at[self.i, cat] = categories_dict[cat]

    @property
    def acc_frame(self) -> pd.DataFrame:
        af: pd.DataFrame = self.row[[i for i in self.row.columns if not i.find(':') == 1]]
        return af

    @property
    def filled_cells(self):
        filled_flag_ser = self.categories.map(pd.notna)
        print(filled_flag_ser)
        filled = self.categories[filled_flag_ser==True]
        return filled

    @property
    def mark(self):
        return self.row.at[self.i, 'DONE']

    @mark.setter
    def mark(self, mark):
        self.row.at[self.i, 'DONE'] = mark

    @property
    def is_mark_filled(self) -> bool:
        return pd.notna(self.mark)

    @property
    def date(self) -> datetime.date:
        return self.row.at[self.i, 'DATE']

    @property
    def need_common_filling(self):
        team_data = self.row.acc_frame.at[self.row.day_index, 'COM']
        flag = True if len(team_data.split(',')) < 1 else False
        return flag

    @property
    def is_empty(self) -> bool:
        nans = [i for i in self.categories if pd.notna(i)]
        return nans == []

    @property
    def is_filled(self) -> bool:
        nans = [i for i in self.row.loc[self.i] if pd.isna(i)]
        return nans == []

    def load_day_row(self):
        self.row = pd.read_excel(self.path_to, index_col=0).fillna(np.nan)
        date = self.row.at[self.i, 'DATE']
        self.row.at[self.i, 'DATE'] = date.date()
        return self

    def concat_row_with(self, existed_row):
        for value in existed_row.categories:
            pass

    def create_row(self, path_to_file):
        with pd.ExcelWriter(
                path_to_file,
                mode='w'
        ) as writer:
            self.row.to_excel(writer)
