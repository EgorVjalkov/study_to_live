import pandas as pd
from typing import Optional

from utils.converter import Converter
from filler.vedomost_cell import VedomostCell
from counter import classes as cl


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
        self.list_of_all_recipient_cells = []

    @property
    def working_cells_index(self) -> pd.Index:
        return pd.Index(self.cell_list_for_working)

    @property
    def accessory_index(self) -> pd.Index: # как источник клеток для coefs и внктриклассово
        return pd.Index([i for i in self.index if i.isupper() and i not in ['DAY', 'STATUS']])

    def get_all_recipient_cells_list(self, recipient: str) -> list:
#        if self.list_of_all_recipient_cells:
#            self.list_of_all_recipient_cells.clear()
#
        date_ser = pd.Series({self.name: self.DAY}, name='DAY')
        r = cl.Recipient(recipient, date_ser)
        acc_frame = pd.DataFrame(self[self.accessory_index]).T
        r.extract_data_by_recipient(acc_frame)
        r.get_with_children_col()
        r_positions = r.get_r_positions_col().at[self.name]

        self.list_of_all_recipient_cells.extend([i for i in self.index if i[0] in r_positions])
        print(self.list_of_all_recipient_cells)
        return self.list_of_all_recipient_cells

    def get_working_cells_index(self, recipient: str, behavior: str) -> pd.Index | list:
        if behavior == 'coefs':
            return self.accessory_index
        else:
            return self.get_all_recipient_cells_list(recipient)

    def filter_by_args_and_load_data(self, recipient: str, behavior: str, price_frame: pd.DataFrame) -> pd.Series:
        self.get_working_cells_index(recipient, behavior)
        for c_name in self.list_of_all_recipient_cells:
            vedomost_cell = VedomostCell(c_name, self[c_name], recipient, price_frame[c_name])
            print('v', vedomost_cell.current_value)
            #print(c_name, vedomost_cell.can_be_filled)

            match behavior, vedomost_cell:
                case 'filling', vc if vc.can_be_filled:
                    self.cell_list_for_working.append(c_name)
                    self[c_name] = vedomost_cell # подумай здесь о много ступенчатом добавлении данных
                case 'correction' | 'count', vc if vc.can_be_corrected:
                    self.cell_list_for_working.append(c_name)
                    self[c_name] = vedomost_cell
                case 'coefs' | 'manually', _:
                    self.cell_list_for_working.append(c_name)
                    self[c_name] = vedomost_cell
        return self

    #@property
    #def filled_recipient_cells_for_working(self) -> pd.Series: # для рeпорта
    #    filled = self[self.recipient_cells_for_working_index].map(lambda i: i.is_filled_now)
    #    return self[filled[filled == True].index]

    @property
    def filled_cells_index(self) -> pd.Index: # для рeпорта
        filled = self[self.working_cells_index].map(lambda i: i.is_filled_now)
        return filled[filled == True].index

    #@property
    #def all_filled_recipient_cells_index(self) -> pd.Index: # для подсчета всех ячееек заполненных реципиентом
    #    #для определения все ли ячейки реципиента заполнены
    #    can_be_filled_ser = self[self.all_recipient_cells_index].map(lambda cell: cell.has_value)
    #    return can_be_filled_ser[can_be_filled_ser==True].index

    #def save_values(self):
    #    for c_name in self.recipient_cells_for_working_index:
    #        if self[c_name].is_filled_now:
    #            self[c_name] = self[c_name].new_v
    #        else:
    #            self[c_name] = self[c_name].current_v
    #    return self

    @property
    def day_row_for_saving(self) -> pd.Series:
        row = self.copy()
        for c_name in row.index:
            match row[c_name]:
                case VedomostCell(is_filled_now=True):
                    row[c_name] = self[c_name].new_v
                case VedomostCell(is_filled_now=False):
                    row[c_name] = self[c_name].current_v
        return row

    @property
    def is_all_r_cells_filled(self):
        return len(self.working_cells_index) == len(self.filled_cells_index)

    @property
    def frame_for_counting(self) -> pd.DataFrame:
        index_for_counting = ['DAY'] + list(self.accessory_index) + list(self.working_cells_index)
        #print(self[self.all_filled_recipient_cells_index])
        return pd.DataFrame({self.name: self.day_row_for_saving[index_for_counting]}).T

    #@property
    #def frame_for_counting(self) -> pd.DataFrame:
    #    index_for_counting = ['DAY'] + list(self.accessory_index) + list(self.all_recipient_cells_index)
    #    return pd.DataFrame({self.name: self[index_for_counting]}).T

    @property
    def date_n_day_str(self):
        date = Converter(date_object=self.name).to('str')
        day_name = day_dict[self['DAY']]
        return f'{date} ({day_name})'
