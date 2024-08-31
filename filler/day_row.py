import datetime
import pandas as pd
from dataclasses import dataclass, InitVar
from typing import Optional

from counter import classes as cl
from utils.converter import Converter
from filler.vedomost_cell import VedomostCell


day_dict = {
    '1': 'понедельник',
    '2': 'вторник',
    '3': 'среда',
    '4': 'четверг',
    '5': 'пятница',
    '6': 'суббота',
    '7': 'воскресенье'
}

class DayRow(pd.Series):
    def __init__(self, day_data: pd.Series):
        super().__init__(day_data)
        self.cell_list_for_working = []
        self.all_recipient_cells_index: Optional[pd.Index] = None

    @property
    def has_done_status_by_another_recipient(self):
        return self.STATUS in cl.r_liters

#    @property
#    def categories(self) -> pd.Series: # для внутриклассового использования
#        categories_index = self.index.map(lambda i: ':' in i)
#        return self[categories_index == True]
#
    @property
    def filled_recipient_cells_for_working(self) -> dict: # для репорта
        # похоже и здесь проблема, некоторые из этих ячеек могут быть незаполнены, но быть не ноне
        # решается через can-be-filled
        filled = self[self.recipient_cells_for_working_index].map(lambda i: i is not None)
        return self[filled[filled == True].index].to_dict()

    @property
    def accessory_index(self) -> pd.Index: # как источник клеток для coefs и внктриклассово
        return pd.Index([i for i in self.index if i.isupper() and i not in ['DAY', 'STATUS']])

    @property
    def recipient_cells_for_working_index(self) -> pd.Index:
        return pd.Index(self.cell_list_for_working)

    @property
    def all_filled_recipient_cells_index(self) -> pd.Index: # для подсчета всех ячееек заполненных реципиентом
        return pd.Index([i for i in self.all_recipient_cells_index if self[i]])

    def get_all_recipient_cells_index(self, recipient: str) -> pd.Index:
        date_ser = pd.Series({self.name: self.DAY}, name='DAY')
        r = cl.Recipient(recipient, date_ser)
        acc_frame = pd.DataFrame(self[self.accessory_index]).T
        r.extract_data_by_recipient(acc_frame)
        r.get_with_children_col()
        r_positions = r.get_r_positions_col().at[self.name]
        self.all_recipient_cells_index = pd.Index([i for i in self.index if i[0] in r_positions])
        return self.all_recipient_cells_index

    def get_working_cells_index(self, recipient: str, behavior: str) -> pd.Index:
        # все равно подтягиваем ячейки реципиента, т. к. при подсчете они все равно потребуются
        if behavior == 'coefs':
            return self.accessory_index
        else:
            return self.all_recipient_cells_index

    def transform_cell_and_append_to_working_list(self, name: str, data: VedomostCell) -> object:
        self[name] = data
        self.cell_list_for_working.append(name)
        return self

    def filter_by_args_and_load_data(self, recipient: str, behavior: str, price_frame: pd.DataFrame) -> pd.Series:
        cells = self.get_working_cells_index(recipient, behavior)
        for c_name in cells:
            vedomost_cell = VedomostCell(c_name, self[c_name], recipient, price_frame[c_name])
            match behavior, vedomost_cell:
                case 'filling', vc if vc.can_be_filled:
                    self.transform_cell_and_append_to_working_list(c_name, vc)
                case 'correction', vc if vc.can_be_corrected:
                    self.transform_cell_and_append_to_working_list(c_name, vc)
                case 'coefs' | 'manually', vc:
                    self.transform_cell_and_append_to_working_list(c_name, vc)
        return self

    def save_values(self):
        for c_name in self.recipient_cells_for_working_index:
            if self[c_name].already_filled:
                self[c_name] = self[c_name].new_v
            else:
                self[c_name] = self[c_name].current_v
        return self

#    @property
#    def is_all_filled(self) -> bool:
#        false_if_none = self.categories.map(lambda i: bool(i)) # все ли клетки имеют значение?
#        return false_if_none[false_if_none == False].empty # пустой ли контейнер, куда сложены все клетки без значения
#
    @property
    def is_all_r_cells_filled(self):
        can_be_filled_ser = self[self.recipient_cells_for_working_index].map(lambda cell: cell.can_be_filled) # eсть ли не заполненные клетки?
        return can_be_filled_ser[can_be_filled_ser == True].empty # пустой ли контейнер, куда сложены все не заполненные клетки

    @property
    def no_recipient_cells_filled(self):
        return self.all_filled_recipient_cells_index.empty

    @property
    def frame_for_counting(self) -> pd.DataFrame:
        index_for_counting = ['DAY'] + list(self.accessory_index) + list(self.all_filled_recipient_cells_index)
        return pd.DataFrame({self.name: self[index_for_counting]}).T

    @property
    def date_n_day_str(self):
        date = Converter(date_object=self.name).to('str')
        day_name = day_dict[self['DAY']]
        return f'{date} ({day_name})'
