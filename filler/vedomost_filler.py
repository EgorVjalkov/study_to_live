import datetime

import pandas as pd
import classes as cl
from filler.vedomost_cell import VedomostCell
from filler.day_row import DayRow
from DB_main import mirror
from temp_db.unfilled_rows_db import UnfilledRowsDB
from utils.converter import Converter


class VedomostFiller:
    def __init__(self,
                 recipient: str = '',
                 behavior: str = ''):

        self.recipient = recipient
        self.behavior = behavior

        self.mark_ser = None
        self.day = None
        self.cells_ser = pd.Series()
        self.path_to_mf = None

        self.active_cell = None

    def __call__(self, *args, **kwargs):
        if mirror.need_update:
            mirror.update_by_date()
        self.mark_ser: pd.Series = mirror.get_dates_for(self.recipient, by_behavior=self.behavior)
        return self

    @property
    def r_sleeptime(self):
        return f'{self.recipient[0].lower()}:sleeptime'

    @ property
    def r_siesta(self):
        return f'{self.recipient[0].lower()}:siesta'

    @property
    def days(self) -> list:
        days = self.mark_ser.index.to_list()
        days: list = [Converter(date_object=date_).to('str') for date_
                      in days]
        return days

    def change_a_day(self, date: datetime.date | str) -> DayRow:
        if isinstance(date, str):
            date = Converter(date_in_str=date).to('date_object')
        day_mark = self.mark_ser.at[date]
        paths_by_date = mirror.get_paths_by(date)
        temp_db = UnfilledRowsDB(*paths_by_date)
        if day_mark in ['empty', 'Y']:
            day_row = temp_db.load_as_('row', by_date=date, from_='mf')
        else:
            day_row = temp_db.load_as_('row', by_date=date, from_='temp_db')
        self.day = DayRow(day_row)
        return self.day

    @property
    def r_positions(self):
        acc_frame = pd.DataFrame(self.day.accessories).T
        r = cl.Recipient(self.recipient)
        r.extract_data_by_recipient(acc_frame)
        r.get_with_children_col()
        r.get_r_positions_col()
        return r.mod_data.at[self.day.date, 'positions']

    def filtering_(self, by_='positions'):
        filtered = list(self.day.categories.index)
        if by_ == 'private':
            filtered = [i for i in filtered
                        if i[0] == self.recipient[0].lower()]

        elif by_ == 'positions':
            filtered = [i for i in filtered
                        if i[0] in self.r_positions]

        else:
            filtered = [i for i in filtered
                        if i == by_]

        return self.day.categories[filtered]

    def get_cells_ser(self, by_: str = 'positions'):
        # нужно попробовать загружать категории по одиночке и сравнить производительность в моменте
        self.cells_ser = self.filtering_(by_)
        prices = mirror.load_prices_by(self.day.date)
        for cat in self.cells_ser.index:
            cell = VedomostCell(prices,
                                self.recipient,
                                name=cat,
                                value=self.cells_ser[cat])
            if self.behavior == 'for filling':
                if cell.can_be_filled:
                    self.cells_ser[cat] = cell

            elif self.behavior == 'for correction':
                if cell.can_be_corrected:
                    self.cells_ser[cat] = cell

            elif self.behavior == 'manually':
                cell.revert_value()
                self.cells_ser[cat] = cell
                self.active_cell = cell.name

        filtered = self.cells_ser.map(lambda i: isinstance(i, VedomostCell))
        self.cells_ser = self.cells_ser[filtered == True]

        return self.cells_ser

    @property
    def unfilled_cells(self):
        unfilled = [i for i in self.cells_ser.index
                    if i not in self.already_filled_dict]
        return unfilled

    @property
    def already_filled_dict(self):
        filled = {}
        if not self.cells_ser.empty:
            filled = self.cells_ser.map(lambda cell: cell.new_value if cell.already_filled else None).to_dict()
            filled = {i: filled[i] for i in filled if filled[i]}
        return filled

    def change_a_cell(self, name_from_tg):
        self.active_cell = name_from_tg
        if self.behavior == 'for correction':
            cell_for_correction = self.cells_ser[self.active_cell]
            cell_for_correction.revert_value()
            self.cells_ser[self.active_cell] = cell_for_correction
        return self.active_cell

    def fill_the_cell(self, value_from_tg) -> object:
        if value_from_tg == 'не мог':
            value_from_tg = 'can`t'
        elif value_from_tg == 'забыл':
            value_from_tg = '!'
        cell: VedomostCell = self.cells_ser[self.active_cell]

        if cell.is_filled:
            cell.new_cat_value = f'{cell.old_value},{self.recipient[0]}{value_from_tg}'

        else:
            if cell.has_private_value:
                cell.new_cat_value = f'{self.recipient[0]}{value_from_tg}'
            else:
                cell.new_cat_value = value_from_tg
        self.cells_ser[cell.name] = cell
        return self

    def collect_data_to_day_row(self):
        # здесь и есть точка входа для записи категории или вспоможенцв
        self.day.categories = self.already_filled_dict
        self.change_done_mark()

    @property
    def is_r_categories_filled(self) -> bool:
        pos_ser = self.filtering_(by_='positions')
        nans = pos_ser[pos_ser.map(lambda i: pd.isna(i)) == True]
        return len(nans) == 0

    def change_done_mark(self):
        if self.day.is_filled:
            self.day.mark = 'Y'
        else:
            if self.is_r_categories_filled:
                self.day.mark = self.recipient[0]
            else:
                self.day.mark = 'at work'

    def count_day_sum(self):
        pass

    @property
    def date_to_str(self):
        return Converter(date_object=self.day.date).to('str')

    @property
    def filled_cells_list_for_print(self):
        return [f'{c} - "{self.already_filled_dict[c]}"'
                for c in self.already_filled_dict]


if __name__ == '__main__':
    for name in ['Lera', 'Egr']:
        filler = VedomostFiller(recipient=name,
                                behavior='for filling')
        filler()
        filler.change_a_day('6.1.24')
        filler.get_cells_ser()
        print(filler.cells_ser)
        #for i in filler.unfilled_cells:
        #    filler.change_a_cell(i)
        #    filler.fill_the_cell('+')
        #print(filler.cells_ser)
        #filler.collect_data_to_day_row()
        #mirror.save_day_data(filler.day)
