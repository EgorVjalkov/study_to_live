import datetime
import pandas as pd
import numpy as np


class DayRow:
    def __init__(self,
                 day_row: pd.DataFrame = pd.DataFrame(),
                 path: str = ''):

        self.day_row: pd.DataFrame = day_row
        self.path_to: str = path

    @property
    def i(self) -> int:
        return self.day_row.index[0]

    @property
    def categories(self) -> pd.Series:
        cf: pd.DataFrame = self.day_row[[i for i in self.day_row.columns if i.find(':') == 1]]
        return cf.loc[self.i]

    @property
    def acc_frame(self) -> pd.DataFrame:
        af: pd.DataFrame = self.day_row[[i for i in self.day_row.columns if not i.find(':') == 1]]
        return af

    @property
    def mark(self):
        return self.day_row.at[self.i, 'DONE']

    @property
    def is_mark_filled(self) -> bool:
        return pd.notna(self.mark)

    @property
    def date(self) -> datetime.date:
        return self.day_row.at[self.i, 'DATE']

    @property
    def need_common_filling(self):
        team_data = self.day_row.acc_frame.at[self.day_row.day_index, 'COM']
        flag = True if len(team_data.split(',')) < 1 else False
        return flag

    @property
    def is_empty(self) -> bool:
        nans = [i for i in self.categories if pd.notna(i)]
        return nans == []

    @property
    def is_filled(self) -> bool:
        nans = [i for i in self.day_row.loc[self.i] if pd.isna(i)]
        return nans == []

    def load_day_row(self):
        self.day_row = pd.read_excel(self.path_to, index_col=0).fillna(np.nan)
        date = self.day_row.at[self.i, 'DATE']
        self.day_row.at[self.i, 'DATE'] = date.date()
        return self

    def create_row(self, path_to_file):
        with pd.ExcelWriter(
                path_to_file,
                mode='w'
        ) as writer:
            self.day_row.to_excel(writer)
