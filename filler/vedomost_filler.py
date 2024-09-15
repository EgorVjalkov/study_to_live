import datetime
import pandas as pd
from typing import Optional

import program2
from DB_main import mirror

from filler.vedomost_cell import VedomostCell
from filler.day_row import DayRow
from filler.date_funcs import today_for_filling
from utils.converter import Converter
from counter import classes as cl


class ResultEmptyError(BaseException):
    pass


class VedomostFiller:
    def __init__(self,
                 recipient: str = '',
                 behavior: str = '',
                 day_data: DayRow = None):

        self.recipient = recipient
        self.behavior = behavior
        self.day: Optional[DayRow] = day_data

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
        return self.day

    def filter_cells(self) -> DayRow:
        self.day.filter_by_args_and_load_data(self.recipient, self.behavior, mirror.get_cells_data(self.behavior))
        return self.day

    @property
    def working_space(self) -> pd.Series:
        return self.day[self.day.working_cells_index]

    @property
    def need_to_fill(self) -> int:
        return len(self.day.working_cells_index)

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
        return not self.day.filled_cells_index.empty

    def update_bd_and_get_dict_for_rep(self, save: bool = True) -> dict:
        if self.behavior not in ['correction', 'count']:
            self.correct_day_status()
        print(self.day.STATUS)
        mirror.set_day_status(self.day)

        filled_cells_index = self.day.filled_cells_index
        match not filled_cells_index.empty, save:
            case True, need_save:
                row_for_saving = self.day.day_row_for_saving
                if need_save:
                    print('not empty, save')
                    mirror.update_vedomost(row_for_saving)
                return row_for_saving[filled_cells_index].to_dict()
        return {}

    def update_status(self) -> None:
        self.correct_day_status()
        mirror.set_day_status(self.day)
        mirror.update_vedomost(self.day.day_row_for_saving)

    @property
    def done_by_another_recipient(self):
        status = self.day.STATUS
        return status != self.recipient[0] and status in cl.r_liters

    def correct_day_status(self) -> object:
        # не сделано исключение по Y, т.к. такой день не может попасть в работу по заполнению
        match self.day.is_all_r_cells_filled, self.done_by_another_recipient:
            case True, True:
                self.day.STATUS = 'Y'
            case True, False:
                self.day.STATUS = self.recipient[0]
            case False, False:
                self.day.STATUS = 'at work'
        return self

    @property
    def mirror_status(self):
        return mirror.status_series[self.day.name]


class CoefsFiller(VedomostFiller):
    def __init__(self, recipient):
        super().__init__(recipient, 'coefs')

    def correct_day_status(self) -> object:
        re_filler = VedomostFiller(recipient=self.recipient,
                                   behavior='filling',
                                   day_data=DayRow(self.day.day_row_for_saving))
        re_filler.filter_cells()
        re_filler.correct_day_status()
        print(self.day.STATUS)
        print(re_filler.day.STATUS)
        self.day.STATUS = re_filler.day.STATUS
        return self


class VedomostCounter(VedomostFiller):
    def __init__(self, recipient: str, day_data: DayRow = None):

        super().__init__(recipient,
                         'count',
                         day_data=day_data)

    def count_day_sum(self):
        self.filter_cells()
        print(self.day)
        frame_for_counting = self.day.frame_for_counting
        print(frame_for_counting)
        #result = program2.main(
        #    recipients=[self.recipient],
        #    data_frame=frame_for_counting,
        #    price_frame=mirror.get_cells_data('filling'),
        #    filled_frame=False,
        #    demo_mode=True,
        #    show_calc=False)

        #result_row = result.loc[self.day.name].map(
        #    lambda i: 0.0 if i in ['can`t', 'wishn`t'] else i)
        #frame_for_counting.loc['result'] = result_row.fillna(0.0)
        #frame_for_counting = frame_for_counting.dropna(axis=1)
        #del frame_for_counting['DAY']
        #frame_for_counting.loc[self.day.name] = (frame_for_counting.loc[self.day.name].
        #                                         map(lambda i: f'"{i}"'))
        #frame_for_counting = frame_for_counting.dropna(axis=1)
        ##frame_for_counting = frame_for_counting[self.day.all_recipient_cells_index].fillna(0.0).T
        return frame_for_counting


if __name__ == '__main__':
    filler = VedomostFiller(recipient='Egr',
                            behavior='correction')

    print(mirror.status_series)
    filler()
    filler.change_day('14.9.24')
    #filler.filter_cells()
    #filler.active_cell = 'e:sleeptime'
    #filler.fill_the_active_cell(None)
    #print(filler.active_cell_data)
    #pre = filler.update_bd_and_get_dict_for_rep(save=False)
    #print(pre)
    #counter = VedomostCounter('Lera', filler.day.day_row_for_saving)
    #rep2 = counter.count_day_sum()
    #print(rep2)
    #counter.filter_cells()


    #filler.change_day('10.9.24')
    #print(filler.working_space)
    #print(filler.day.STATUS)
    ##filler.filter_cells()
    ##filler.active_cell = 'a:stroll'
    ##filler.fill_the_active_cell('can`t')
    #rep = filler.update_bd_and_get_dict_for_rep(save=True)
    #print(rep)

