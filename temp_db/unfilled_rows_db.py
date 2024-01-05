import datetime
import pandas as pd
import os
from pathlib import Path


class UnfilledRowsDB:
    def __init__(self,
                 path_to_temp_db: Path,
                 path_to_mf=None):

        self.path_to_temp_db = path_to_temp_db
        self.path_to_mf = path_to_mf
        self.month_db = None

    def load_as_(self,
                 data_type: str,
                 by_date=None,
                 from_: str = '') -> pd.Series | pd.DataFrame:
        if data_type == 'mf' or from_ == 'mf':
            path = self.path_to_mf
        else:
            path = self.path_to_temp_db
        frame_: pd.DataFrame = pd.read_excel(path, sheet_name='vedomost')
        frame_['DATE'] = frame_['DATE'].map(lambda _date: _date.date())
        frame_ = frame_.set_index('DATE')
        if data_type == 'row':
            return frame_.loc[by_date]
        else:
            return frame_

    def save_(self, frame: pd.DataFrame, as_: str, mode: str):
        if as_ == 'mf':
            path = self.path_to_mf
        else:
            path = self.path_to_temp_db
        if mode == 'a':
            if_sheet_exist = 'replace'
        else:
            if_sheet_exist = None

        with pd.ExcelWriter(
            path,
            mode=mode,
            if_sheet_exists=if_sheet_exist
        ) as writer:
            frame.to_excel(writer, sheet_name='vedomost')

    def del_filled_row(self, day_date: datetime.date) -> object:
        temp_frame = self.temp_db_from_file
        print(day_date)
        temp_frame = temp_frame[temp_frame.index != day_date]
        self.save_(temp_frame, as_='temp_db', mode='a')
        return self

    @property
    def mf_from_file(self):
        return self.load_as_('mf')

    @property
    def temp_db_from_file(self):
        return self.load_as_('temp_db')

    @staticmethod
    def get_unfilled_rows_from_(df: pd.DataFrame, by_date: datetime.date) -> pd.DataFrame:
        unfilled_rows: pd.DataFrame = df[df.index <= by_date]
        unfilled_rows = unfilled_rows[unfilled_rows['STATUS'] != 'Y']
        return unfilled_rows

    def get_actual_dayrows_df_(self,
                               from_: str,
                               by_date: datetime.date) -> pd.DataFrame:
        mf = self.mf_from_file
        unfilled_rows: pd.DataFrame = self.get_unfilled_rows_from_(mf, by_date)
        if not unfilled_rows.empty:
            if not from_ == 'mf':
                temp_db = self.temp_db_from_file
                for date in temp_db.index:
                    unfilled_rows.loc[date] = temp_db.loc[date]
        return unfilled_rows
