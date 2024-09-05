import datetime
import pandas as pd
from typing import Optional

import program2
from DB_main import mirror

from filler.vedomost_cell import VedomostCell
from filler.day_row import DayRow
from filler.date_funcs import today_for_filling
from utils.converter import Converter


class ResultEmptyError(BaseException):
    pass


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

    def change_day(self, date: str | datetime.date) -> DayRow:
        if isinstance(date, str):
            date = Converter(date_in_str=date).to('date_object')
        mirror.check_date(date)
        if self.behavior != 'count':
            mirror.occupy(date)
        self.day = DayRow(mirror.get_day_row(date))
        self.day.get_all_recipient_cells_index(self.recipient)
        return self.day

    def filter_cells(self) -> DayRow:
        self.day.filter_by_args_and_load_data(self.recipient, self.behavior, mirror.get_cells_data(self.behavior))
        return self.day

    @property
    def working_space(self) -> pd.Series:
        return self.day[self.day.recipient_cells_for_working_index]

    @property
    def need_to_fill(self) -> int:
        return len(self.day.recipient_cells_for_working_index)

    @property
    def categories_btns(self):
        return [i.btn for i in self.working_space]

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
        translation_dict = {'не мог': 'can`t', 'забыл': '!'}
        value_from_tg = translation_dict.get(value_from_tg, value_from_tg)

        self.active_cell_data.fill(value_from_tg)
        return self

    @property
    def something_done(self) -> bool:
        return not self.day.filled_recipient_cells_for_working.empty

    #@property
    #def already_filled_dict(self):
    #    #return {cell.name: cell.new_value for cell in self.working_space if cell.already_filled}
    #    filled = {cell.name: cell.new_value for cell in self.working_space if cell.already_filled}
    #    return filled

    def update_day_row(self) -> object:
        if self.behavior in ['filling', 'manually']:
            self.correct_day_status()
        mirror.update_vedomost(self.day.day_row_for_saving)
        return self

    def correct_day_status(self) -> object:
        match self.day:
            #здесь тоже замутки. дни со статусом Y переделываются в имееные.
            case DayRow(is_all_r_cells_filled=True, has_done_status_by_another_recipient=True):
                self.day.STATUS = 'Y'
            case DayRow(is_all_r_cells_filled=True, has_done_status_by_another_recipient=False):
                self.day.STATUS = self.recipient[0]
            case DayRow(is_all_r_cells_filled=False, has_done_status_by_another_recipient=False):
                self.day.STATUS = 'at work'
        return self

    def count_day_sum(self):
        if self.behavior == 'coefs':
            self.day.get_all_recipient_cells_index(self.recipient)

        #if not self.day.no_recipient_cells_filled:
        if not self.something_done:
            raise ResultEmptyError

        else:
            frame_for_counting = self.day.frame_for_counting
            print(frame_for_counting)
            result = program2.main(
                recipients=[self.recipient],
                data_frame=frame_for_counting,
                price_frame=mirror.get_cells_data('filling'),
                filled_frame=False,
                demo_mode=True,
                show_calc=False)

            result_row = result.loc[self.day.name].map(
                lambda i: 0.0 if i in ['can`t', 'wishn`t'] else i)
            frame_for_counting.loc['result'] = result_row.fillna(0.0)
            frame_for_counting.loc[self.day.name] = (frame_for_counting.loc[self.day.name].
                                                     map(lambda i: f'"{i}"'))
            frame_for_counting = frame_for_counting[self.day.all_filled_recipient_cells_index].fillna(0.0)

            index_with_filled_marks = frame_for_counting.columns.map(
                lambda i: f'*{i}' if i in self.day.filled_recipient_cells_for_working else i)
            frame_for_counting = pd.DataFrame({'mark': frame_for_counting.loc[self.day.name].to_list(),
                                               'result': frame_for_counting.loc['result'].to_list()},
                                              index=index_with_filled_marks)
            return frame_for_counting


if __name__ == '__main__':
    #filler = VedomostFiller(recipient='Egr',
    #                        behavior='coefs')
    filler = VedomostFiller(recipient='Lera',
                            behavior='filling')

# сделай дэйроу через проперти в котором только значения будут и его сохранишь в бд, а в стоковом пусить будут ячейки
# а значит и функционал без костылей!!!

# почемуто не всегда делает  отметки в мирроре, приглядись
    #mirror.date = datetime.date(day=31, month=8, year=24)
    filler()
    filler.change_day('1.9.24')
    filler.filter_cells()
    print(filler.day.all_filled_recipient_cells_index)
    print(filler.day.is_all_r_cells_filled)
    #filler.active_cell = 'a:stroll'
    #filler.fill_the_active_cell('1')
    #filler.count_day_sum()
    #print(filler.day)
