import pandas as pd
from pathlib import Path
import os
from row_db.mirror_db import yesterday, today


class UnfilledRowsDB:
    def __init__(self, data_frame: pd.DataFrame):
        self.month_bd = data_frame

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

    @staticmethod
    def replace_temp_db(mother_frame: pd.DataFrame) -> pd.DataFrame:
        unfilled_rows: pd.DataFrame = mother_frame[mother_frame['DATE'] <= today]
        unfilled_rows: pd.DataFrame = unfilled_rows[unfilled_rows['DONE'] != 'Y']
        db_from_mf = unfilled_rows
        if yesterday not in db_from_mf['DATE'].values:
            yesterday_row: pd.DataFrame = mother_frame[mother_frame['DATE'] == yesterday]
            db_from_mf = pd.concat([yesterday_row, db_from_mf]).sort_index()
        return db_from_mf

    @staticmethod
    def save_temp_db(path: Path, temp_db: pd.DataFrame):
        with pd.ExcelWriter(path=path,
                            mode='w',
                            engine='openpyxl',
                            ) as writer:
            temp_db.to_excel(writer, index=True)

    # есть мыслишка, что надо в зеркале оставлять ссылку на материнский фрейм. и если в бд их заявлено 2, сверять с обоими
    # и уже потом поступать как надо

    def update(self):
        dbs = {}
        if not self.contains(PathMaker(today).to_months_temp_db):
            mf = self.get_frame(path=PathMaker(today).to_vedomost, sheet_name='vedomost')
            dbs[PathMaker().to_months_temp_db] = self.replace_temp_db(mf)

        mirror: pd.DataFrame = self.mirror_frame
        paths: pd.DataFrame = mirror.get(['path_to_mf', 'path_to_db']).drop_duplicates()
        print(paths)
        for row in paths.index:
            # замуть с индексацией
            paths = paths.loc[row]
            print(paths)
            path_to_mf, path_to_db = paths[0], paths[1]
            mf = self.get_frame(path=path_to_mf, sheet_name='vedomost')
            if (not self.contains(path_to_db) |
                    self.mf_is_newer_than_db(path_to_db, path_to_mf)):
                dbs[path_to_db] = self.replace_temp_db(mf)
            else:
                temp_db = self.get_frame(path_to_db)
                dbs[path_to_db] = self.update_temp_db(mf, temp_db)

        for path in dbs:
            self.save_temp_db(path, dbs[path])

        #mother_frame = self.mother_frame
        #print(self.mother_frame)
        #self.save_temp_db(temp_db)

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
