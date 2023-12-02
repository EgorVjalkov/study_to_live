import pandas as pd
import datetime
import classes as cl
from VedomostCell import VedomostCell
from path_maker import PathBy
from day_row import DayRow
from row_db.DB_main import day_db


class VedomostFiller:
    def __init__(self,
                 recipient: str = '',
                 behavior: str = '',
                 date: datetime.date = datetime.date.today()):

        self.date = date
        self.path_to_mother_frame = PathBy(self.date).to_vedomost
        self.path_to_temp_db = PathBy().to_temp_db

        # поле переменных для работы функций

        self.day: DayRow = DayRow()
        self.recipient: str = recipient
        self.row_index_ser = None
        self.cells_ser: pd.Series = pd.Series()
        self.behavior: str = behavior

        self.active_cell = None

    def __call__(self, *args, **kwargs):
        day_db.update()
        self.row_index_ser: pd.Series = day_db.load_rows_for(self.recipient, self.behavior)
        return self

    @ property
    def r_sleeptime(self):
        return f'{self.recipient[0].lower()}:sleeptime'

    @ property
    def r_siesta(self):
        return f'{self.recipient[0].lower()}:siesta'

    @property
    def days(self) -> list:
        return self.row_index_ser.index.to_list()

    def change_the_day_row(self, date_form_tg):
        self.day = DayRow(path=self.row_index_ser[date_form_tg]).load_day_row()
        return self.day

    @property
    def r_positions(self):
        r = cl.Recipient(self.recipient)
        r.extract_data_by_recipient(self.day.acc_frame)
        r.get_with_children_col()
        r.get_r_positions_col()
        return r.mod_data.at[self.day.i, 'positions']

    def filtering_by(self, positions=False, category=None, only_private_categories=False):
        filtered = list(self.day.categories.index)
        if only_private_categories:
            filtered = [i for i in filtered
                        if i[0] == self.recipient[0].lower()]
        elif category:
            filtered = [i for i in filtered
                        if i == category]
        elif positions:
            filtered = [i for i in filtered
                        if i[0] in self.r_positions]

        self.cells_ser = \
            self.day.categories[filtered]
        return self.cells_ser

    def get_cells_ser(self):
        prices = pd.read_excel(self.path_to_mother_frame, sheet_name='price', index_col=0)
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
        unfilled = [i for i in self.cells_ser.index if i not in self.already_filled_dict]
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

    def fill_the_cell(self, value_from_tg):
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

    def collect_data_to_day_row(self):
        self.day.categories = self.already_filled_dict
        self.change_done_mark()

    def change_done_mark(self):
        if self.day.is_filled:
            self.day.mark = 'Y'
        else:
            if not self.unfilled_cells:
                self.day.mark = self.recipient[0]
            else:
                self.day.mark = 'at work'

    def count_day_sum(self):
        pass

    @property
    def changed_date(self):
        date = self.day.date
        date = datetime.date.strftime(date,  '%d.%m.%y')
        return date

    @property
    def filled_cells_list_for_print(self):
        return [f'{c} - "{self.already_filled_dict[c]}"'
                for c in self.already_filled_dict]


if __name__ == '__main__':
    day_db.update()
    #filler = VedomostFiller(recipient='Egr',
    #                        behavior='for filling')
    #filler()
    #print(filler.row_index_ser)
    #print(filler.days)
    #filler.change_the_day_row('27.11.23')
    #filler.filtering_by(positions=True)
    #filler.get_cells_ser()
    #print(filler.day.filled_cells)
    #for i in filler.unfilled_cells:
    #    filler.change_a_cell(i)
    #    filler.fill_the_cell('+')
    #print(filler.day.filled_cells)

    #filler.collect_data_to_day_row()
    #day_db.create_row(filler.day)
    #print(filler.row_db.vedomost)
    #print(filler.is_row_filled)
    #print(filler.cell_names_list)
    #if filler.is_row_filled:
    #    filler.save_day_data_to_mother_frame()
    #else:
    #    filler.save_day_data_to_temp_db()
