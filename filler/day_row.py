import datetime
import pandas as pd
from dataclasses import dataclass, InitVar

from counter import classes as cl
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


@dataclass
class DayRow:
    row: InitVar[pd.Series]
    for_: InitVar[str]
    by_: InitVar[str]

    def __post_init__(self, row, for_, by_):
        accessories_index = [i for i in row.index if i.isupper()]
        accessories = row[accessories_index]

        if by_ == 'coefs':
            self.row: pd.Series = accessories

        else:
            date = row.name
            date_ser = pd.Series({date: row['DAY']}, name='DAY')

            r = cl.Recipient(for_, date_ser)
            acc_frame = pd.DataFrame(accessories).T
            r.extract_data_by_recipient(acc_frame)
            r.get_with_children_col()
            r_positions = r.get_r_positions_col().at[date]

            index = ['STATUS']+[i for i in row.index if i[0] in r_positions]
            self.row: pd.Series = row[index]

    def __repr__(self):
        date_ = Converter(date_object=self.date).to('str')
        return f'DayRow {date_}: {self.mark}(filled: {self.filled_cells.index.to_list()})'

    @property
    def mark(self):
        return self.row.at['STATUS']

    @mark.setter
    def mark(self, mark):
        self.row.at['STATUS'] = mark

    @property
    def date(self) -> datetime.date | Hashable:
        return self.row.name

    # мжет быть здесь только индекс сделать
    @property
    def cells(self) -> list:
        return [i for i in self.row.index if i not in ['DAY', 'STATUS']]

    #@cells.setter
    #def cells(self, cells_ser: pd.Series):
    #    for cell_name in cells_ser.index:
    #        self.row[cell_name] = cells_ser[cell_name]

    @property
    def date_n_day_dict(self):
        day = self.row.at['DAY']
        day_name = day_dict[day]
        date = Converter(date_object=self.date).to('str')
        return {date: day_name}

    @property
    def filled_cells(self):
        filled_flag_ser = self.cells.map(pd.notna)
        filled = self.cells[filled_flag_ser == True]
        return filled

    @property
    def is_filled(self) -> bool:
        nans = [i for i in self.row if pd.isna(i)]
        return nans == []

    @property
    def frame(self) -> pd.DataFrame:
        row_with_date = pd.concat([pd.Series({'DATE': self.date}),
                                   self.row], axis=0)
        frame = pd.DataFrame(data=row_with_date, index=[0]).set_index('DATE')
        return frame

    #def get_available_positions(self, recipient: str) -> list | set:
    #    acc_frame = pd.DataFrame(self.accessories).T
    #    date_ser = pd.Series({self.date: self.row['DAY']}, name='DAY')
    #    r = cl.Recipient(recipient, date_ser)
    #    r.extract_data_by_recipient(acc_frame)
    #    r.get_with_children_col()
    #    r_positions = r.get_r_positions_col().at[self.date]
    #    return r_positions

    #def filter_by_available_positions(self, avail_pos):
    #    filtered = self.row.index.map(
    #        lambda i: i.islower() and i[0] not in avail_pos)
    #    self.row = self.row[filtered == False]
    #    return self.row

    #def filter_by_available_positions(self, recipient: str, behavior: str) -> pd.Series:
    #    if behavior == 'coefs':
    #        return self.accessories

    #    acc_frame = pd.DataFrame(self.accessories).T
    #    date_ser = pd.Series({self.date: self.row['DAY']}, name='DAY')
    #    r = cl.Recipient(recipient, date_ser)
    #    r.extract_data_by_recipient(acc_frame)
    #    r.get_with_children_col()
    #    r_positions = r.get_r_positions_col().at[self.date]
    #    filtered = self.row.index.map(
    #        lambda i: ':' in i and i[0] in r_positions)
    #    self.row = self.row[filtered == True]
    #    return self.row
