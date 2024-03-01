import datetime
import os
import pathlib
from pathlib import Path


def make_dir_if_not_exist(path_: Path):
    if not path_.exists():
        os.mkdir(path_)


class PathMaker:
    def __init__(self):
        path_to_home = pathlib.Path.home()
        self.path_to_project = Path(path_to_home, 'study_to_live')

    @property
    def temp_db(self):
        path_to_temp_db_dir = Path(self.path_to_project, 'temp_db', 'temp_db')
        make_dir_if_not_exist(path_to_temp_db_dir)
        return path_to_temp_db_dir

    @staticmethod
    def get_month(date: datetime.date) -> str:
        return date.strftime('%b%y').lower()

    def mother_frame_by(self, date: datetime.date):
        month = self.get_month(date)
        path_to_vedomost_dir = Path(self.path_to_project, 'months', month)
        make_dir_if_not_exist(path_to_vedomost_dir)
        path_to_vedomost_xlsx = Path(path_to_vedomost_dir, f'{month}.xlsx')
        return path_to_vedomost_xlsx

    def months_temp_db_by(self, date: datetime.date):
        month = self.get_month(date)
        path_to_temp_db_file = Path(self.temp_db, f'{month}_temp_db.xlsx')
        return path_to_temp_db_file


path_to = PathMaker()
path_to_project = path_to.path_to_project


if __name__ == '__main__':
    date = datetime.date(month=2, day=1, year=2024)
    p = path_to.mother_frame_by(date)
    p2 = path_to.months_temp_db_by(date)
    print(p, p2)
