import datetime
import pandas as pd
import classes as cl

from utils.converter import Converter
from typing import Hashable


day_dict = {
    1: 'понедельник',
    2: 'вторник',
    3: 'среда',
    4: 'четверг',
    5: 'пятница',
    6: 'суббота',
    7: 'воскресенье'
}


class DayRow:
    def __init__(self, day_row: pd.Series = pd.Series(dtype='object')):
        self.row = day_row

    def __repr__(self):
        date_ = Converter(date_object=self.date).to('str')
        return f'DayRow {date_}: {self.mark}(filled: {self.filled_cells.index.to_list()})'

    @property
    def categories(self) -> pd.Series:
        cat = self.row.index.map(lambda i: i.find(':') == 1)
        cat = self.row[cat == True]
        return cat

    @categories.setter
    def categories(self, categories: dict):
        for cat in categories:
            self.row.at[cat] = categories[cat]

    @property
    def accessories(self) -> pd.Series:
        acc = self.row.index.map(lambda i: not i.find(':') == 1 and i not in ['DAY', 'STATUS'])
        acc = self.row[acc == True]
        return acc

    @property
    def date_n_day_dict(self):
        day = self.row.at['DAY']
        day_name = day_dict[day]
        date = Converter(date_object=self.date).to('str')
        return {date: day_name}

    @property
    def filled_cells(self):
        filled_flag_ser = self.categories.map(pd.notna)
        filled = self.categories[filled_flag_ser == True]
        return filled

    @property
    def is_filled(self) -> bool:
        nans = [i for i in self.row if pd.isna(i)]
        return nans == []

    @property
    def mark(self):
        return self.row.at['STATUS']

    @mark.setter
    def mark(self, mark):
        self.row.at['STATUS'] = mark

    @property
    def date(self) -> datetime.date | Hashable:
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
    def frame(self) -> pd.DataFrame:
        row_with_date = pd.concat([pd.Series({'DATE': self.date}),
                                   self.row], axis=0)
        frame = pd.DataFrame(data=row_with_date, index=[0]).set_index('DATE')
        return frame

    def get_available_positions(self, recipients: list) -> list | set:
        acc_frame = pd.DataFrame(self.accessories).T
        date_ser = pd.Series({self.date: self.row['DAY']}, name='DAY')
        pos_set = set()
        for rec in recipients:
            r = cl.Recipient(rec, date_ser)
            r.extract_data_by_recipient(acc_frame)
            r.get_with_children_col()
            r_positions = r.get_r_positions_col().at[self.date]

            if len(recipients) == 1:
                return r_positions

            else:
                r_set = set(r_positions)
                pos_set.update(r_set)

        return pos_set

    def filter_by_available_positions(self, avail_pos):
        filtered = self.row.index.map(
            lambda i: i.islower() and i[0] not in avail_pos)
        self.row = self.row[filtered == False]
        return self.row
