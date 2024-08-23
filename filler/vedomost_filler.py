import datetime
import pandas as pd
import numpy as np
from typing import Optional

from counter import program2
from DB_main import mirror

from filler.vedomost_cell import VedomostCell
from filler.day_row import DayRow
from filler.date_funcs import today_for_filling
from filler.recipient import Recipient
from temp_db.unfilled_rows_db import DataBase
from utils.converter import Converter


class VedomostFiller:
    def __init__(self,
                 recipient: str = '',
                 behavior: str = ''):

        self.recipient = recipient
        self.behavior = behavior

        self.day: Optional[DayRow] = None
        self.active_cell_name: Optional[str] = None

    def __call__(self, *args, **kwargs) -> object:
        mirror.date = today_for_filling()
        return self

    @property
    def r_sleeptime(self):
        return f'{self.recipient[0].lower()}:sleeptime'

    @property
    def r_siesta(self):
        return f'{self.recipient[0].lower()}:siesta'

    @property
    def day_btns(self) -> list:
        days = mirror.get_dates_for(self.recipient, self.behavior).to_list()
        days: list = [Converter(date_object=date_).to('str') for date_
                      in days]
        days = [[i] for i in days] #для геттера по item
        return days

    def change_day_and_filter_cells(self, date: str | datetime.date) -> DayRow:
        if isinstance(date, str):
            date = Converter(date_in_str=date).to('date_object')
        mirror.check_date(date)
        mirror.occupy(date)
        self.day = DayRow(mirror.get_day_row(date))
        self.day.load_cell_data(self.recipient, self.behavior, mirror.get_cells_data(self.behavior))
        return self.day

    @property
    def working_space(self) -> pd.Series:
        return self.day[self.day.working_cells]

    @property
    def need_to_fill(self):
        return bool(self.day.working_cells)

    @property
    def categories_btns(self):
        return [self.day.row[i].btn for i in self.working_space]

    @property
    def active_cell(self) -> str:
        return self.active_cell_name

    @active_cell.setter
    def active_cell(self, cell_name):
        self.active_cell_name = cell_name

    @property
    def active_cell_data(self) -> VedomostCell:
        return self.day[self.active_cell]

    @active_cell_data.setter
    def active_cell_data(self, cell_data: VedomostCell):
        self.day[self.active_cell] = cell_data

    def fill_the_active_cell(self, value_from_tg) -> object:
        if self.behavior in ['correction', 'coefs']:
            self.active_cell_data = self.active_cell_data.revert()

        translation_dict = {'не мог': 'can`t', 'забыл': '!'}
        value_from_tg = translation_dict.get(value_from_tg, value_from_tg)

        self.active_cell_data.fill(value_from_tg)
        return self

    @property
    def something_done(self) -> None | bool:
        for cell in self.working_space:
            if cell.already_filled:
                return True

    @property
    def already_filled_dict(self):
        #return {cell.name: cell.new_value for cell in self.working_space if cell.already_filled}
        filled = {cell.name: cell.new_value for cell in self.working_space if cell.already_filled}
        return filled

    def correct_day_status(self):
        if self.day.is_filled:
            self.day.mark = 'Y'
        else:
            if self.is_r_categories_filled:
                self.day.mark = self.recipient[0]
            else:
                self.day.mark = 'at work'

    #def update_day_row(self):
    #    self.day.cells = self.already_filled_dict # <- очень удачно пишет все!
    #    if self.behavior != 'coefs':
    #        self.correct_day_status()
    #    else:
    #        mirror.release(self.day)
    #    print(self.day)
    #    print(mirror.status_series)
    #    return self.day

    @property
    def acc_in_str(self) -> list:
        rep = self.day.date_n_day_dict
        rep.update(self.day.accessories.to_dict())
        for i in self.already_filled_dict:
            del rep[i]
            new_i = '*'+i
            rep[new_i] = self.already_filled_dict[i]
        return [f'{i}: "{rep[i]}"' for i in rep]

    def count_day_sum(self):
        columns = [i for i in self.day.row.index if ':' not in i]
        columns.extend(self.cells_ser.index)
        r_frame = pd.DataFrame(self.day.row[columns].to_dict(), index=[self.day.date])

        result = program2.main(
            recipients=[self.recipient],
            data_frame=r_frame,
            price_frame=mirror.load_prices_by(self.day.date, 'filling'),
            filled_frame=False,
            demo_mode=True,
            show_calc=False)

        result_row = result.loc[self.day.date]
        result_row = result_row.replace('can`t', 0)
        r_frame.loc['result'] = result_row
        r_frame = r_frame[self.cells_ser.index].T.replace(np.nan, 0)
        return r_frame

    @property
    def date_to_str(self):
        return Converter(date_object=self.day.date).to('str')

    def filled_cells_list_for_print(self, dict_=()) -> list:
        if not dict_:
            dict_ = self.already_filled_dict
        return [f'{c} -> {dict_[c]}' for c in dict_]


if __name__ == '__main__':
    filler = VedomostFiller(recipient='Egr',
                            behavior='coefs')

    filler()
    #print(mirror.date)
    filler.change_day_and_filter_cells('20.8.24')
    print(filler.working_space)
    filler.active_cell = 'a:stroll'
    filler.active_cell_data.current_value = 'EF'
    print(filler.active_cell_data.revert())
    print(filler.working_space)
    print(filler.day)


    #filler.active_cell_data.recipient = 'Lera'
    #print(filler.active_cell_data)
    #filler.active_cell_data.fill('F')
    #print(filler.active_cell_data)
    #filler.fill_the_active_cell('1')
    #print(filler.active_cell_data)


