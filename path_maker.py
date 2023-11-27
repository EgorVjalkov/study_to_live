import datetime
import os
import pathlib
from pathlib import Path


def make_dir_if_not_exist(path_: Path):
    if not path_.exists():
        os.mkdir(path_)


class PathToVedomost:
    def __init__(self, date: datetime.date = datetime.date.today()):
        self.date: datetime.date = date

    @property
    def path_to_project(self):
        return pathlib.Path.cwd()

    @property
    def month(self):
        return self.date.strftime('%b%y').lower()

    @property
    def to_vedomost(self):
        path_to_vedomost_dir = Path(self.path_to_project, 'months', self.month)
        make_dir_if_not_exist(path_to_vedomost_dir)
        path_to_vedomost_xlsx = Path(path_to_vedomost_dir, f'{self.month}.xlsx')
        return path_to_vedomost_xlsx

    @property
    def to_temp_db(self):
        temp_dir = f'temp_db'
        path_to_temp_db = Path(self.path_to_project, 'row_db', temp_dir)
        make_dir_if_not_exist(path_to_temp_db)
        return path_to_temp_db


if __name__ == '__main__':
    path = PathToVedomost()
    p = path.to_vedomost
    p2 = path.to_temp_db
    print(p, p2)
