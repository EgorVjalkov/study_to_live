import datetime
import pandas as pd
from dataclasses import dataclass, InitVar
from typing import Optional

from counter import classes as cl
from utils.converter import Converter
from filler.vedomost_cell import VedomostCell


day_dict = {
    1: 'понедельник',
    2: 'вторник',
    3: 'среда',
    4: 'четверг',
    5: 'пятница',
    6: 'суббота',
    7: 'воскресенье'
}


class DayRow(pd.Series):
    def __init__(self, day_data: pd.Series):
        super().__init__(day_data)
        self.index_for_working: list = []

    def __repr__(self):
        date_ = Converter(date_object=self.name).to('str')
        return f'DayRow {date_}: {self.STATUS}(working on: {self.working_cells})'

    @property
    def working_cells(self):
        return self.index_for_working

    @working_cells.setter
    def working_cells(self, seq: list):
        self.index_for_working = seq

    @property
    def accessory_index(self):
        return [i for i in self.index if i.isupper() and i not in ['DAY', 'STATUS']]

    def set_working_categories(self, recipient: str) -> list:
        date_ser = pd.Series({self.name: self.DAY}, name='DAY')
        r = cl.Recipient(recipient, date_ser)
        acc_frame = pd.DataFrame(self[self.accessory_index]).T
        r.extract_data_by_recipient(acc_frame)
        r.get_with_children_col()
        r_positions = r.get_r_positions_col().at[self.name]
        return [i for i in self.index if i[0] in r_positions]

    def set_working_cells(self, recipient: str, behavior: str):
        if behavior == 'coefs':
            cells = self.accessory_index
        else:
            cells = self.set_working_categories(recipient)
        return cells

    def set_cell(self, name: str, data: VedomostCell) -> object:
        self[name] = data
        self.working_cells.append(name)
        return self

    def load_cell_data(self, recipient: str, behavior: str, price_frame: pd.DataFrame) -> pd.Series:
        cells = self.set_working_cells(recipient, behavior)
        for c_name in cells:
            vedomost_cell = VedomostCell(c_name, self[c_name], recipient, price_frame[c_name])
            match behavior, vedomost_cell:
                case 'filling', vc if vc.can_be_filled:
                    self.set_cell(c_name, vc)
                case 'correction', vc if vc.can_be_corrected:
                    self.set_cell(c_name, vc)
                case 'coefs' | 'manually', vc:
                    self.set_cell(c_name, vc)
        return self

#    @property
#    def date_n_day_dict(self):
#        day = self.row.at['DAY']
#        day_name = day_dict[day]
#        date = Converter(date_object=self.date).to('str')
#        return {date: day_name}
#
#    @property
#    def filled_cells(self):
#        filled_flag_ser = self.cells.map(pd.notna)
#        filled = self.cells[filled_flag_ser == True]
#        return filled
#
#    @property
#    def is_filled(self) -> bool:
#        nans = [i for i in self.row if pd.isna(i)]
#        return nans == []
#
#    @property
#    def frame(self) -> pd.DataFrame:
#        row_with_date = pd.concat([pd.Series({'DATE': self.date}),
#                                   self.row], axis=0)
#        frame = pd.DataFrame(data=row_with_date, index=[0]).set_index('DATE')
#        return frame
#
