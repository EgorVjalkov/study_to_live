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
        self.all_recipient_cells_index: list = []

    @property
    def recipient_cells_for_working(self):
        return self.index_for_working

    @recipient_cells_for_working.setter
    def recipient_cells_for_working(self, seq: list):
        self.index_for_working = seq

    @property
    def categories_index(self):
        return [i for i in self.index if ':' in i]

    @property
    def accessory_index(self):
        return [i for i in self.index if i.isupper() and i not in ['DAY', 'STATUS']]

    @property
    def recipient_cells_with_value_index(self) -> list:
        return [i for i in self[self.all_recipient_cells_index].index if self[i]]


    def get_all_recipient_cells_index(self, recipient: str) -> object:
        date_ser = pd.Series({self.name: self.DAY}, name='DAY')
        r = cl.Recipient(recipient, date_ser)
        acc_frame = pd.DataFrame(self[self.accessory_index]).T
        r.extract_data_by_recipient(acc_frame)
        r.get_with_children_col()
        r_positions = r.get_r_positions_col().at[self.name]
        self.all_recipient_cells_index = [i for i in self.index if i[0] in r_positions]
        return self.all_recipient_cells_index

    def get_working_cells_index(self, recipient: str, behavior: str):
        if behavior == 'coefs':
            cells = self.accessory_index
        else:
            cells = self.get_all_recipient_cells_index(recipient)
        return cells

    def set_cell(self, name: str, data: VedomostCell) -> object:
        self[name] = data
        self.recipient_cells_for_working.append(name)
        return self

    def filter_by_args_and_load_data(self, recipient: str, behavior: str, price_frame: pd.DataFrame) -> pd.Series:
        cells = self.get_working_cells_index(recipient, behavior)
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

    def save_values(self):
        for c_name in self.recipient_cells_for_working:
            if self[c_name].already_filled:
                self[c_name] = self[c_name].new_v
            else:
                self[c_name] = self[c_name].current_v
        return self

    @property
    def is_all_filled(self) -> bool:
        return not bool([i for i in self[self.categories_index] if not i])

    @property
    def is_r_cells_filled(self) -> bool:
        print([i for i in self[self.recipient_cells_for_working] if not i])
        return not bool([i for i in self[self.recipient_cells_for_working] if not i])

    @property
    def frame_for_counting(self) -> pd.DataFrame:
        index_for_counting = ['DAY'] + self.accessory_index + self.recipient_cells_with_value_index
        return pd.DataFrame({self.name: self[index_for_counting]}).T

    @property
    def date_n_day_dict(self):
        date = Converter(date_object=self.name).to('str')
        return {date: self['DAY']}
