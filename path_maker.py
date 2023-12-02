import datetime
import os
import pathlib
from pathlib import Path


def make_dir_if_not_exist(path_: Path):
    if not path_.exists():
        os.mkdir(path_)


class PathBy:
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
        path_to_temp_db_dir = Path(self.path_to_project, 'temp_db')
        make_dir_if_not_exist(path_to_temp_db_dir)
        return path_to_temp_db_dir

    @property
    def to_months_temp_db(self):
        path_to_temp_db_file = Path(self.to_temp_db, f'{self.month}_temp_db.xlsx')
        return path_to_temp_db_file


if __name__ == '__main__':
    path = PathBy()
    p = path.to_vedomost
    p2 = path.to_temp_db
    print(p, p2)
