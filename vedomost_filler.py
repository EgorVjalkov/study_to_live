import pandas as pd
import numpy as np
import datetime
import classes as cl
from analytic_utilities import FrameForAnalyse
from VedomostCell import VedomostCell
#from bot_main import cell
# важная тема с заполнением: неодходимо прописать как быть с многочленными категориями, типо мытья посуды или прогулок
# задроч с путем надо подумать как его слеоать!
# хрень с классом Сell


ff = FrameForAnalyse()


class VedomostFiller:
    def __init__(self, path='', recipient=''):
        self.path_to_mother_frame = path
        self.md_instrument = cl.MonthData()

        # поле переменных для работы функций
        self.mother_frame = pd.DataFrame()
        self.prices = pd.DataFrame()
        self.r_vedomost = pd.DataFrame()

        self.day_row = pd.DataFrame()
        self.day_row_index = None
        self.recipient = recipient
        self.r_cats_ser_by_positions = pd.Series()
        self.non_filled_cells_df = pd.DataFrame()

        self.active_cell = None

    @property
    def admin(self):
        return True if self.recipient == 'Egr' else False

    def get_mother_frame_and_prices(self, path_to_mother_frame=None):
        if path_to_mother_frame:
            self.path_to_mother_frame = path_to_mother_frame
        print(self.path_to_mother_frame)
        self.mother_frame = self.md_instrument.load_and_prepare_vedomost(self.path_to_mother_frame)
        self.prices = self.md_instrument.get_price_frame(self.path_to_mother_frame)

    def get_r_name_and_limiting(self, r_name):
        self.recipient = r_name
        self.r_vedomost = self.md_instrument.limiting('for filling', self.recipient)

    @property
    def days_for_filling(self):
        days_in_str_ser = self.r_vedomost['DATE'].map(lambda d: datetime.date.strftime(d, '%d.%m.%y')).to_dict()
        return {days_in_str_ser[i]: i for i in days_in_str_ser}

    def change_the_day_row(self, date_form_tg):
        self.day_row_index = self.days_for_filling[date_form_tg]
        self.md_instrument.vedomost = self.r_vedomost.loc[self.day_row_index:self.day_row_index]
        self.day_row = self.md_instrument
        self.day_row.get_frames_for_working()
        return self.day_row

    @property
    def r_positions(self):
        r = cl.Recipient(self.recipient, self.day_row.date)
        r.get_and_collect_r_name_col(self.day_row.accessory['COM'], 'children')
        r.get_and_collect_r_name_col(self.day_row.accessory['PLACE'], 'place')
        r.get_and_collect_r_name_col(self.day_row.accessory['DUTY'], 'duty')
        r.get_family_col()
        r.get_r_positions_col()
        return r.mod_data.at[self.day_row_index, 'positions']

    def filtering_by_positions(self):
        if not self.day_row.vedomost.empty:
            filtered = [i for i in self.day_row.categories.columns
                        if i[0] in self.r_positions]
            self.r_cats_ser_by_positions = self.day_row.categories.loc[self.day_row_index][filtered]
        return self.r_cats_ser_by_positions

# затрах с нонфиледом.
    def get_non_filled_cells_df(self):
        self.r_cats_ser_by_positions = self.r_cats_ser_by_positions.replace('!', np.nan)
        print(self.r_cats_ser_by_positions)
        non_filled = self.r_cats_ser_by_positions.to_dict()
        for cat in non_filled:
            cell = VedomostCell(self.prices,
                                self.recipient,
                                name=cat,
                                value=non_filled[cat])
            if cell.is_filled: # прoверка на заполненность
                if cell.can_append_data: # проверка на возможность дописывания в яйчейку
                    self.non_filled_cells_df[cell.cat_name] = cell.extract_cell_data()
            else:
                self.non_filled_cells_df[cell.cat_name] = cell.extract_cell_data()
        return self.non_filled_cells_df

    @property
    def non_filled_names_list(self):
        non_filled = self.non_filled_cells_df.loc['new_value'].map(lambda e: pd.notna(e))
        non_filled_list = [i for i in non_filled.index if non_filled[i]]
        return non_filled_list

    @property
    def recipient_all_filled_flag(self):
        if not self.non_filled_names_list:
            return True
        else:
            return False

# ежно здесь подумать как переплести Cell и Filler
    def change_a_cell(self, name_from_tg):
        self.active_cell = name_from_tg
        return self.active_cell

    def fill_the_cell(self, value_from_tg):
        if value_from_tg == 'не мог':
            value_from_tg = 'can`t'
        elif value_from_tg == 'забыл':
            value_from_tg = '!'
        cell_ser = self.non_filled_cells_df[self.active_cell]
        print(cell_ser)
        if cell_ser['is_filled']:
            self.non_filled_cells_df.loc['new_value'][self.active_cell] = \
                    f'{cell_ser["old_value"]},{self.recipient[0]}{value_from_tg}'
        else:
            if cell_ser['has_private_value']:
                self.non_filled_cells_df.loc['new_value'][self.active_cell] = \
                    f'{self.recipient[0]}{value_from_tg}'
            else:
                self.non_filled_cells_df.loc['new_value'][self.active_cell] = value_from_tg

    def save_day_data(self):
        new_value_row = self.non_filled_cells_df.loc['new_value']
        for c in new_value_row.index:
            self.day_row.vedomost.loc[self.day_row_index][c]\
                = new_value_row.loc[c]

        self.mother_frame[self.day_row_index:self.day_row_index+1]\
            = self.day_row.vedomost

        if self.recipient_all_filled_flag:
            if pd.notna(self.mother_frame.at[self.day_row_index, 'DONE']):
                self.mother_frame.at[self.day_row_index, 'DONE'] = 'Y'
            else:
                self.mother_frame.at[self.day_row_index, 'DONE'] = self.recipient[0]

        with pd.ExcelWriter(
                self.path_to_mother_frame,
                mode='a',
                engine='openpyxl',
                if_sheet_exists='replace'
        ) as mf_writer:
            self.mother_frame.to_excel(mf_writer, sheet_name='vedomost', index=False)


if __name__ == '__main__':
    month = 'oct23'
    #pd.reset_option('display.max.columns')
    filler = VedomostFiller(path=f'months/{month}/{month}.xlsx')
    filler.get_mother_frame_and_prices()
    filler.get_r_name_and_limiting('Egr')

    filler.change_the_day_row('16.10.23')
    filler.filtering_by_positions()
    filler.get_non_filled_cells_df()
    print(filler.non_filled_names_list)
    for i in filler.non_filled_cells_df:
        print(filler.non_filled_names_list)
        filler.change_a_cell(i)
        filler.fill_the_cell('5')
    filler.change_a_cell('z:stroll')
    filler.fill_the_cell('2')
    filler.save_day_data()
##    print(filler.day_row.vedomost)
##    print(filler.mother_frame.loc[14:15])
##