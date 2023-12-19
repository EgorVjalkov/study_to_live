import datetime
import pandas as pd
from pathlib import Path
import os
from date_constants import yesterday, today


class UnfilledRowsDB:
    def __init__(self,
                 path_to_temp_db: Path,
                 path_to_mf=None,
                 data_frame=None):

        self.path_to_temp_db = path_to_temp_db
        self.path_to_mf = path_to_mf
        self.month_db = data_frame

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
        temp_frame = temp_frame[temp_frame.index != day_date]
        self.save_(temp_frame, as_='temp_db', mode='a')
        return self

    @property
    def mf_from_file(self):
        return self.load_as_('mf')

    @property
    def temp_db_from_file(self):
        return self.load_as_('temp_db')

    # нужен ли нам сеттер???
    @temp_db_from_file.setter
    def temp_db_from_file(self, db):
        self.month_db = db

    def init_temp_db(self) -> pd.DataFrame:
        mother_frame = self.mf_from_file
        unfilled_rows: pd.DataFrame = mother_frame[mother_frame.index <= today]
        unfilled_rows: pd.DataFrame = unfilled_rows[unfilled_rows['DONE'] != 'Y']
        if yesterday in mother_frame.index and yesterday not in unfilled_rows.index:
            yesterday_row: pd.DataFrame = mother_frame[mother_frame['DATE'] == yesterday]
            unfilled_rows = pd.concat([yesterday_row, unfilled_rows]).sort_index()
        self.month_db = unfilled_rows
        return self.month_db


    @staticmethod
    def mf_is_newer_than_db(path_to_mf: Path, path_to_db: Path) -> bool:
        date_temp_db = os.path.getmtime(path_to_db)
        date_mf_db = os.path.getmtime(path_to_mf)
        return date_mf_db > date_temp_db # <- материнский новее

    @staticmethod
    def update_temp_db(mother_frame: pd.DataFrame,
                       temp_db: pd.DataFrame) -> pd.DataFrame:
        date_filter = mother_frame['DATE'].map(lambda date_: date_ in (yesterday, today))
        update_from_mf = mother_frame[date_filter == True]
        for i in update_from_mf.index:
            if i not in temp_db.index:
                temp_db.loc[i] = update_from_mf.loc[i]
        return temp_db

#    def update(self):
#        dbs = {}
#        if not self.contains(PathMaker(today).to_months_temp_db):
#            mf = self.get_frame(path=PathMaker(today).to_vedomost, sheet_name='vedomost')
#            dbs[PathMaker().to_months_temp_db] = self.replace_temp_db(mf)
#
#        mirror: pd.DataFrame = self.mirror_frame
#        paths: pd.DataFrame = mirror.get(['path_to_mf', 'path_to_db']).drop_duplicates()
#        print(paths)
#        for row in paths.index:
#            # замуть с индексацией
#            paths = paths.loc[row]
#            print(paths)
#            path_to_mf, path_to_db = paths[0], paths[1]
#            mf = self.get_frame(path=path_to_mf, sheet_name='vedomost')
#            if (not self.contains(path_to_db) |
#                    self.mf_is_newer_than_db(path_to_db, path_to_mf)):
#                dbs[path_to_db] = self.replace_temp_db(mf)
#            else:
#                temp_db = self.get_frame(path_to_db)
#                dbs[path_to_db] = self.update_temp_db(mf, temp_db)
#
#        for path in dbs:
#            self.save_temp_db(path, dbs[path])
#
#        #mother_frame = self.mother_frame
#        #print(self.mother_frame)
#        #self.save_temp_db(temp_db)
#
#    def create_row(self, row: DayRow) -> DayRow:
#        if self.contains(row.date):
#            full_path: Path = self.get_full_path(row.date)
#            print(full_path)
#            if full_path in self.empty_rows_paths:
#                os.remove(full_path)
#            else:
#                existed_row: DayRow = DayRow(path=full_path).load_day_row()
#                print(f'existed {existed_row}')
#                row.concat_row_with(existed_row)
#
#        if row.is_mark_filled:
#            path_to_file = Path(self.path_to_db, f'{date_part}({row.mark}).xlsx')
#        else:
#            if row.is_empty:
#                path_to_file = Path(self.path_to_db, f'{date_part}(empty).xlsx')
#            else:
#                path_to_file = Path(self.path_to_db, f'{date_part}.xlsx')
#        row.create_row(path_to_file)
