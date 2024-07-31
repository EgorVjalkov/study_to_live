import datetime
import pandas as pd
import classes as cl
import program2

from typing import Optional

from filler.vedomost_cell import VedomostCell
from filler.day_row import DayRow
from DB_main import mirror
from temp_db.unfilled_rows_db import MonthDB
from utils.converter import Converter


class BusyError(BaseException):
    pass


class VedomostFiller:
    def __init__(self,
                 recipient: str = '',
                 behavior: str = ''):

        self.recipient = recipient
        self.behavior = behavior

        self.mark_ser: Optional[pd.Series] = None
        self.day: Optional[DayRow] = None
        self.cells_ser = pd.Series(dtype=object)
        self.active_cell_name: Optional[str] = None

    def __call__(self, *args, **kwargs):
        if self.behavior == 'coefs':
            self.mark_ser = mirror.get_days_for_coef_correction()
        else:
            if mirror.need_update:
                print('need_update')
                print(f'{mirror.need_update}')
                mirror.update_by_date()
            self.mark_ser = mirror.get_dates_for(self.recipient, by_behavior=self.behavior)
        print(self.mark_ser)
        return self

    @property
    def active_cell(self) -> str:
        return self.active_cell_name

    @active_cell.setter
    def active_cell(self, cell_name):
        self.active_cell_name = cell_name

    @property
    def active_cell_data(self) -> VedomostCell:
        return self.cells_ser[self.active_cell_name]

    @active_cell_data.setter
    def active_cell_data(self, cell_data: VedomostCell):
        self.cells_ser[self.active_cell_name] = cell_data

    @property
    def r_sleeptime(self):
        return f'{self.recipient[0].lower()}:sleeptime'

    @property
    def sleeptime_is_empty(self):
        if self.day:
            if self.r_sleeptime not in self.already_filled_dict:
                if pd.isna(self.day.row[self.r_sleeptime]):
                    return True
        else:
            return False

    @property
    def r_siesta(self):
        return f'{self.recipient[0].lower()}:siesta'

    @property
    def need_work(self):
        return not self.mark_ser.empty

    @property
    def days(self) -> list:
        days = self.mark_ser.index.to_list()
        days: list = [Converter(date_object=date_).to('str') for date_
                      in days]
        days = [[i] for i in days] #для геттера по item
        return days

    def change_a_day(self, date: str | datetime.date) -> DayRow:
        if isinstance(date, str):
            date = Converter(date_in_str=date).to('date_object')

        day_mark = self.mark_ser[date]
        if day_mark == 'busy':
            raise BusyError

        mirror.occupy(date)

        paths_by_date = mirror.get_paths_by(date)
        temp_db = MonthDB(*paths_by_date)

        if day_mark in ['empty', 'Y']:
            from_ = 'mf'

        else:
            from_ = 'temp_db'

        print(f'LOAD: {day_mark} --> {from_}')
        day_row = temp_db.load_as_('row', by_date=date, from_=from_)
        self.day = DayRow(day_row)
        avail_pos_for_all_recipients = self.day.get_available_positions(cl.RECIPIENTS)
        self.day.filter_by_available_positions(avail_pos_for_all_recipients)

        # если есть катуи не заполняемые, но данная фильтрация их фикусит в кант
        # if cant_cats.hasnans:
        #     cant_cats = cant_cats.fillna('can`t')
        #     self.day.categories = cant_cats.to_dict()
        # print(self.day.categories)

        return self.day

    def filtering_(self, series=pd.Series(dtype=str), by_='positions'):
        if by_ == 'coefs':
            return self.day.accessories
        else:
            filtered = list(self.day.categories.index)
            if by_ == 'positions':
                r_positions = self.day.get_available_positions([self.recipient])
                filtered = [i for i in filtered if i[0] in r_positions]
            else:
                filtered = [i for i in filtered if i == by_]

        if not series.empty:
            return series[filtered]
        else:
            return self.day.categories[filtered]

    def get_cells_ser(self, by_: str = 'positions'):
        # нужно попробовать загружать категории по одиночке и сравнить производительность в моменте
        if self.behavior == 'coefs':
            self.cells_ser = self.filtering_(by_='coefs')
        else:
            self.cells_ser = self.filtering_(by_=by_)

        prices = mirror.load_prices_by(self.day.date, for_=self.behavior)

        for cat in self.cells_ser.index:
            cell = VedomostCell(prices,
                                self.recipient,
                                name=cat,
                                value=self.cells_ser[cat])
            if self.behavior == 'filling':
                if cell.can_be_filled:
                    self.cells_ser[cat] = cell

            elif self.behavior == 'correction':
                if cell.can_be_corrected:
                    self.cells_ser[cat] = cell

            elif self.behavior == 'manually':
                cell.revert()
                self.cells_ser[cat] = cell
                self.active_cell_name = cell.name

            else:
                self.cells_ser[cat] = cell

        filtered = self.cells_ser.map(lambda i: isinstance(i, VedomostCell))
        self.cells_ser = self.cells_ser[filtered == True]

        return self.cells_ser

    @property
    def need_to_fill(self):
        return len(self.cells_ser)

    def get_bnts_of_categories(self) -> list:
        return [i.btn for i in self.cells_ser]

    @property
    def something_done(self):
        for cell in self.cells_ser:
            if cell.already_filled:
                return True

    @property
    def already_filled_dict(self):
        filled = self.cells_ser.map(lambda cell: cell.new_value if cell.already_filled else None).to_dict()
        filled = {i: filled[i] for i in filled if filled[i]}
        return filled

    def fill_the_active_cell(self, value_from_tg) -> object:
        if self.behavior in ['correction', 'coefs']:
            self.active_cell_data = self.active_cell_data.revert()

        translation_dict = {'не мог': 'can`t', 'забыл': '!'}
        value_from_tg = translation_dict.get(value_from_tg, value_from_tg)

        self.active_cell_data = self.active_cell_data.fill(value_from_tg)
        return self

    def change_done_mark(self):
        if self.day.is_filled:
            self.day.mark = 'Y'
        else:
            if self.is_r_categories_filled:
                self.day.mark = self.recipient[0]
            else:
                self.day.mark = 'at work'

    def update_day_row(self):
        self.day.categories = self.already_filled_dict # <- очень удачно пишет все!
        if self.behavior != 'coefs':
            self.change_done_mark()
        else:
            mirror.release(self.day)
        print(self.day)
        print(mirror.series)
        return self.day

    @property
    def is_r_categories_filled(self) -> bool:
        pos_ser = self.filtering_(by_='positions')
        nans = pos_ser[pos_ser.map(lambda i: pd.isna(i)) == True]
        return len(nans) == 0

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
        dict_ = self.day.row.to_dict()
        frame = pd.DataFrame(dict_, index=[self.day.date])
        #print(frame.index)
        result = program2.main(
            recipients=[self.recipient],
            data_frame=frame,
            price_frame=mirror.load_prices_by(self.day.date, 'filling'),
            filled_frame=False,
            demo_mode=True,
            show_calc=False)

        result_row = result.loc[self.day.date]
        categories = self.filtering_(by_='positions').map(lambda i: f'"{i}"')
        result_row = self.filtering_(series=result_row, by_='positions').replace('can`t', 0)
        result_row.name = 'result'
        result_frame = pd.concat([categories, result_row], axis=1)
        return result_frame

    @property
    def date_to_str(self):
        return Converter(date_object=self.day.date).to('str')

    def filled_cells_list_for_print(self, dict_=()) -> list:
        if not dict_:
            dict_ = self.already_filled_dict
        return [f'{c} -> {dict_[c]}' for c in dict_]


if __name__ == '__main__':
#    filler = VedomostFiller(recipient='Lera',
#                            behavior='filling')
#    filler()
#    print(filler.mark_ser)
#    filler.change_a_day('17.7.24')
#    print(filler.mark_ser)
#
    filler = VedomostFiller(recipient='Lera',
                            behavior='correct')
    filler()
    print(filler.mark_ser)
    filler.change_a_day('22.7.24')
    filler.get_cells_ser()
    print(filler.cells_ser)
    print(filler.get_bnts_of_categories())
    #print(filler.cells_ser)
    #for i in filler.cells_ser:

    #    filler.change_a_cell('a:pipi')
    #    filler.fill_the_cell('0')
    ##print(filler.cells_ser)
    #filler.collect_data_to_day_row()
    #print(filler.count_day_sum())


    #mirror.save_day_data(filler.day)
