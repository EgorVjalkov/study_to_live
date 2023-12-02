import datetime
import pandas as pd
import os
from pathlib import Path
from path_maker import PathBy
from day_row import DayRow


today: datetime.date = datetime.date.today()
yesterday: datetime.date = today - datetime.timedelta(days=1)


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


class Mirror:
    def __init__(self, frame: pd.DataFrame):
        #self.frame: pd.DataFrame = pd.DataFrame()
        self.frame = frame
        self.path_to_db = PathBy().to_temp_db

    def update_by_date(self):
        last_day = self.frame['DATE'].max(axis=0)
        last_day_index = max(self.frame.index)
        delta = today - last_day
        for day in range(1, delta.days+1):
            date = last_day + datetime.timedelta(days=day)
            done = 'empty'
            index = last_day_index + day
            self.frame = pd.concat([self.frame,
                                    pd.DataFrame({'DATE': date, 'DONE': done},
                                                 index=[index])])
        print(self.frame)

    def update(self, dbs: list):
        mirrors = []
        for db in dbs:
            frame = db.get(['DATE', 'DONE'])
            frame['date_from_tg'] = frame['DATE'].map(
                lambda date_: Converter(date_object=date_).to('str'))
            frame['row_index'] = frame.index
            frame['path_to_mf'] = frame['DATE'].map(lambda date_: PathBy(date=date_).to_vedomost)
            frame['path_to_db'] = frame['DATE'].map(lambda date_: PathBy(date=date_).to_months_temp_db)
            mirrors.append(frame)
        if len(mirrors) > 1:
            self.frame = pd.concat(mirrors)
        else:
            self.frame = mirrors[0]
        return self.frame


mirror = Mirror(pd.DataFrame(
    {'DATE': datetime.date(year=2023, month=12, day=1), 'DONE': 'L'},
    index=[0]))

print(mirror.frame)
mirror.update_by_date()




class UnfilledRowsDB:
    def __init__(self):
        self.path_to_db = PathBy().to_temp_db
        self.mirror = None

    def __repr__(self):
        s_for_print: pd.Series = self.mirror_frame.set_index('date_from_tg')['DONE']
        list_ = [f'{i}: {s_for_print[i]}' for i in s_for_print.index]
        return f'DB({", ".join(list_)})'

    @property
    def months_db_paths(self) -> list:
        files = os.listdir(self.path_to_db)
        return [Path(self.path_to_db, file_name) for file_name in files]

    @property
    def mirror_frame(self) -> pd.DataFrame:
        self.mirror = pd.DataFrame()
        dbs = []
        if self.months_db_paths:
            for p in self.months_db_paths:
                dbs.append(self.get_frame(p))
            self.mirror: pd.DataFrame = Mirror().update(dbs)
        return self.mirror

    @staticmethod
    def get_frame(path, sheet_name='') -> pd.DataFrame:
        if sheet_name:
            frame: pd.DataFrame = pd.read_excel(path, sheet_name=sheet_name)
        else:
            frame: pd.DataFrame = pd.read_excel(path)
        #print(frame)
        frame['DATE'] = frame['DATE'].map(lambda date_: date_.date())
        return frame

    def contains(self, path_to_db):
        return path_to_db in self.months_db_paths

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
        if not self.contains(PathBy(today).to_months_temp_db):
            mf = self.get_frame(path=PathBy(today).to_vedomost, sheet_name='vedomost')
            dbs[PathBy().to_months_temp_db] = self.replace_temp_db(mf)

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

    def load_rows_for(self, recipient: str, by_behavior: str) -> pd.Series:
        if by_behavior == 'for filling':
            r_done_mark = recipient[0]
            days_frame: pd.DataFrame = self.mirror[self.mirror['DONE'] != r_done_mark]
        elif by_behavior == 'for correction':
            days_frame: pd.DataFrame = self.mirror[self.mirror['DONE'] != 'empty']
            days_frame: pd.DataFrame = days_frame[days_frame['DATE'] >= yesterday]
        else:
            days_frame: pd.DataFrame = self.mirror[self.mirror['DATE'] == today]
        return days_frame.set_index('date_from_tg')['row_index']
