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
        self.r_filling_ser = pd.Series()
        self.non_filled_categories = []

        self.filling_now_cell = None

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
            self.r_filling_ser = self.day_row.categories.loc[self.day_row_index][filtered]
        return self.r_filling_ser

# затрах с нонфиледом.
    def get_non_filled_categories(self):
        self.r_filling_ser = self.r_filling_ser.replace('!', np.nan)
        print(self.r_filling_ser)
        non_filled = self.r_filling_ser.to_dict()
        for cat in non_filled:
            cell.cat_name, cell.cat_value = cat, non_filled[cat]
            if not cell.is_empty: # прoверка на пустоту
                if cell.has_private_value: # проверка на именные значения
                    if cell.can_append_data: # проверка на возможность дописывания в яйчейку
                        self.non_filled_categories.append(cat)
            else:
                self.non_filled_categories.append(cat)
        return self.non_filled_categories

    def delete_filled_category(self, cat_name):
        self.non_filled_categories.remove(cat_name)

    @property
    def recipient_all_filled_flag(self):
        if not self.non_filled_categories:
            return True
        else:
            return False

# ежно здесь подумать как переплести Cell и Filler
    def change_a_cell(self, VedomostCell_object):
        self.filling_now_cell = VedomostCell_object
        self.filling_now_cell.cat_value = self.r_filling_ser[self.filling_now_cell.name]
        # self.delete_filled_category(self.filling_now_cell.cat_name)
        return self.filling_now_cell

    def fill_the_cell(self, new_value):
        if new_value == 'не мог':
            new_value = 'can`t'
        elif new_value == 'забыл':
            new_value = '!'

        #print(self.filling_now_cell.cat_name,
        #      self.filling_now_cell.cat_value,
        #      self.filling_now_cell.is_empty,
        #      self.filling_now_cell.has_private_value)

        if self.filling_now_cell.is_empty:
            if self.filling_now_cell.has_private_value:
                self.r_filling_ser.at[self.filling_now_cell.cat_name] = \
                    f'{self.recipient[0]}{new_value}'
            else:
                self.r_filling_ser.at[self.filling_now_cell.cat_name] = new_value

        else:
            self.r_filling_ser.at[self.filling_now_cell.cat_name] = \
                f'{self.filling_now_cell.cat_value},{self.recipient[0]}{new_value}'

        return self.filling_now_cell

    def save_day_data(self):
        for c in self.r_filling_ser.index:
            self.day_row.vedomost.loc[self.day_row_index, c] = self.r_filling_ser[c]

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
    cell = VedomostCell(filler.prices, num_of_recipietns=2)
    filler.get_r_name_and_limiting('Egr')

    filler.change_the_day_row('16.10.23')
    filler.filtering_by_positions()
    filler.get_non_filled_categories()
    for i in filler.non_filled_categories:
        cell.name = i
        filler.change_a_cell(cell)
        filler.fill_the_cell(new_value='5')
        # тут есть баги!!!!!
        filler.get_non_filled_categories()
        print(filler.non_filled_categories)
    print(filler.r_filling_ser)
    filler.save_day_data()
#    print(filler.day_row.vedomost)
#    print(filler.mother_frame.loc[14:15])
#