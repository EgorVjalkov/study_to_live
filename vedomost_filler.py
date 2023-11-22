import pandas as pd
import datetime
import classes as cl
from VedomostCell import VedomostCell
from path_maker import PathToVedomost
from day_row import DayRow
from row_db.DB_main import day_db


class VedomostFiller:
    def __init__(self,
                 recipient: str = '',
                 behavior: str = ''):

        self.date = datetime.date.today()
        self.path_to_mother_frame = PathToVedomost(self.date).to_vedomost
        self.path_to_temp_db = PathToVedomost().to_temp_db

        # поле переменных для работы функций

        self.day_row: DayRow = DayRow()
        self.recipient = recipient
        self.day_path_dict: list = []
        self.r_cats_ser_by_positions = pd.Series()
        self.cells_df = pd.DataFrame()
        self.behavior = behavior

        self.active_cell = None

    def __call__(self, *args, **kwargs):
        mf: pd.DataFrame = pd.read_excel(self.path_to_mother_frame, sheet_name='vedomost')
        mf['DATE'] = mf['DATE'].map(lambda date: date.date())
        day_db.update(mf)
        self.day_path_dict = day_db.load_rows_dict_for(self.recipient, self.behavior)
        return self

    @ property
    def r_sleeptime(self):
        return f'{self.recipient[0].lower()}:sleeptime'

    @ property
    def r_siesta(self):
        return f'{self.recipient[0].lower()}:siesta'

    #    days = self.r_vedomost['DATE'].to_dict()
    #    if self.behavior:
    #        if self.behavior == 'for filling':
    #            days = {i: days[i] for i in days if days[i] <= datetime.date.today()}

    #        elif self.behavior == 'for correction':
    #            today = datetime.date.today()
    #            yesterday = today - datetime.timedelta(days=1)
    #            categories_f = self.r_vedomost.get(
    #                [cat for cat in self.r_vedomost if cat.islower()])

    #            days_index = [i for i in days if days[i] in [yesterday, today]] #находим индекс вчера и сегодня
    #            days_index = [i for i in days_index                         # проверяем по индексу
    #                          if not all(categories_f.loc[i].map(pd.isna))] # нужно ли что то корректированть

    #            days = {i: days[i] for i in days_index}

    #    days = {datetime.date.strftime(days[d], '%d.%m.%y'): d
    #            for d in days}
    #    return days

    def change_the_day_row(self, date_form_tg):
        print(self.day_path_dict)
        self.day_row = DayRow(path=self.day_path_dict[date_form_tg])
        print(self.day_row.date, self.day_row.mark, self.day_row.acc_frame, self.day_row.categories)
        return self.day_row

    @property
    def r_positions(self):
        r = cl.Recipient(self.recipient)
        r.extract_data_by_recipient(self.day_row.acc_frame)
        r.get_with_children_col()
        r.get_r_positions_col()
        return r.mod_data.at[self.day_row.i, 'positions']

    def filtering_by(self, positions=False, category=None, only_private_categories=False):
        filtered = list(self.day_row.categories.index)
        print(filtered)
        if only_private_categories:
            filtered = [i for i in filtered
                        if i[0] == self.recipient[0].lower()]
        elif category:
            filtered = [i for i in filtered
                        if i == category]
        elif positions:
            filtered = [i for i in filtered
                        if i[0] in self.r_positions]

        self.r_cats_ser_by_positions = \
            self.day_row.categories[filtered]
        return self.r_cats_ser_by_positions

    def get_cells_df(self):
        prices = pd.read_excel(self.path_to_mother_frame, sheet_name='price', index_col=0)
        non_filled = self.r_cats_ser_by_positions.to_dict()
        for cat in non_filled:
            cell = VedomostCell(prices,
                                self.recipient,
                                name=cat,
                                value=non_filled[cat])
            if self.behavior == 'for filling':
                if cell.can_be_filled:
                    # print(cell.name, cell.old_value)
                    # print(cell.can_be_filled)
                    self.cells_df[cell.cat_name] = cell.extract_cell_data()

            elif self.behavior == 'for correction':
                if cell.can_be_corrected:
                    self.cells_df[cell.cat_name] = cell.extract_cell_data()

            elif self.behavior == 'manually':
                cell.revert_value()
                self.cells_df[cell.cat_name] = cell.extract_cell_data()
                self.active_cell = cell.cat_name

        return self.cells_df

    @property
    def cell_names_list(self):
        non_filled_list = []
        if not self.cells_df.empty:
            if self.behavior == 'for filling':
                non_filled = self.cells_df.loc['new_value'].map(lambda v: v is None)
                non_filled_list = [i for i in non_filled.index if non_filled[i]]
            else:
                non_filled_list = list(self.cells_df.columns)
                # вот здесь коллизия: нужно решить как сделать: если я делаю мануальное, то у меня заполняется селл_намес
                # лист, а значит пробиается флаг на полное заполнение, ставится ложная метка! нужно фиксить
        return non_filled_list

    @property
    def already_filled_dict(self):
        filled = []
        if not self.cells_df.empty:
            old = self.cells_df.loc['old_value'].to_dict()
            new = self.cells_df.loc['new_value'].to_dict()
            new = {i: new[i] for i in new if new[i]}
            filled = {i: new[i] for i in new if new[i] != old[i]}
        return filled

    def change_a_cell(self, name_from_tg):
        self.active_cell = name_from_tg
        if self.behavior == 'for correction':
            old_value = self.cells_df.at['old_value', self.active_cell]
            print(old_value)
            cell_for_correction = VedomostCell(self.prices,
                                               self.recipient,
                                               name=self.active_cell,
                                               value=old_value)
            cell_for_correction.revert_value()
            self.cells_df[self.active_cell] = cell_for_correction.extract_cell_data()

        return self.active_cell

    def fill_the_cell(self, value_from_tg):
        if value_from_tg == 'не мог':
            value_from_tg = 'can`t'
        elif value_from_tg == 'забыл':
            value_from_tg = '!'
        cell_ser = self.cells_df[self.active_cell]

        if cell_ser['is_filled']:
            self.cells_df.at['new_value', self.active_cell] = \
                f'{cell_ser["old_value"]},{self.recipient[0]}{value_from_tg}'

        else:
            if cell_ser['has_private_value']:
                self.cells_df.at['new_value', self.active_cell] = \
                    f'{self.recipient[0]}{value_from_tg}'
            else:
                self.cells_df.at['new_value', self.active_cell] = value_from_tg

    def collect_data_to_day_row(self):
        for c in self.already_filled_dict:
            self.day_row.vedomost.at[self.row_in_process_index, c] \
                = self.already_filled_dict[c]
        self.change_done_mark()

    def change_done_mark(self):
        if self.is_row_filled:
            self.day_row.vedomost.at[self.row_in_process_index, 'DONE'] = 'Y'
        else:
            if not self.cell_names_list:
                self.day_row.vedomost.at[self.row_in_process_index, 'DONE'] = self.recipient[0]

    def count_day_sum(self):
        pass

    def save_day_data_to_temp_db(self):
        mark: str = self.day_row.vedomost.at[self.row_in_process_index, 'DONE']
        date: str = self.changed_date.replace('.', '_')
        if pd.notna(mark):
            file_name = f'{date}_{mark}.xlsx'
        else:
            file_name = f'{date}.xlsx'
        # нужно замутить замену файлов временных

        file_path = f'{self.path_to_temp_db}/{file_name}'
        with pd.ExcelWriter(
                file_path,
                mode='w',
                engine='openpyxl'
        ) as temp_writer:
            self.day_row.vedomost.to_excel(temp_writer, sheet_name='vedomost', index=False)

    def save_day_data_to_mother_frame(self):
        self.mother_frame[self.row_in_process_index:self.row_in_process_index + 1] \
            = self.day_row.vedomost
        with pd.ExcelWriter(
                self.path_to_mother_frame,
                mode='a',
                engine='openpyxl',
                if_sheet_exists='replace'
        ) as mf_writer:
            self.mother_frame.to_excel(mf_writer, sheet_name='vedomost', index=False)

    @property
    def changed_date(self):
        date = self.day_row.date.at[self.row_in_process_index, 'DATE']
        date = datetime.date.strftime(date,  '%d.%m.%y')
        return date

    @property
    def filled_cells_list_for_print(self):
        return [f'{i} - "{self.already_filled_dict[i]}"'
                for i in self.already_filled_dict]

    def refresh_day_row(self):
        self.day_row = pd.DataFrame()
        self.row_in_process_index = None
        self.r_cats_ser_by_positions = pd.Series()
        self.cells_df = pd.DataFrame()
        self.active_cell = None


if __name__ == '__main__':
    filler = VedomostFiller(recipient='Egr',
                            behavior='manually')
    filler()
    print(filler.day_path_dict)
    #filler.change_the_day_row('21.11.23')
    #filler.filtering_by(positions=True)
    #filler.get_cells_df()
    #for i in filler.cell_names_list:
    #    filler.change_a_cell(i)
    #    filler.fill_the_cell('+')

    ##filler.collect_data_to_day_row()
    #print(filler.row_db.vedomost)
    #print(filler.is_row_filled)
    #print(filler.cell_names_list)
    #if filler.is_row_filled:
    #    filler.save_day_data_to_mother_frame()
    #else:
    #    filler.save_day_data_to_temp_db()
