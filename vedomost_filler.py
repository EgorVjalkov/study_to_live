import pandas as pd
import datetime
import classes as cl
from analytic_utilities import FrameForAnalyse
#from bot_main import cell
# важная тема с заполнением: неодходимо прописать как быть с многочленными категориями, типо мытья посуды или прогулок
# задроч с путем надо подумать как его слеоать!
# хрень с классом Сell


ff = FrameForAnalyse()


class VedomostCell:
    def __init__(self, price_frame, num_of_recipietns, name=''):
        self.prices = price_frame
        self.name = name
        self.num_of_recipients = num_of_recipietns
        self.value = None

    @property
    def cat_name(self):
        return self.name

    @cat_name.setter
    def cat_name(self, category_name):
        self.name = category_name

    @property
    def cat_value(self):
        return self.value

    @cat_value.setter
    def cat_value(self, value):
        self.value = value

    @property
    def category_data(self):
        cat_data = self.prices[self.cat_name]
        return cat_data

    @property
    def type(self):
        return self.category_data.loc['type']

    @property
    def description(self):
        descr_list = self.category_data.get(['description', 'hint']).to_list()
        descr_list = [e for e in descr_list if e]
        return descr_list

    @property
    def keys(self):
        if 'range' in self.type:
            keys = list(eval(self.type))
        elif self.type == 'dict':
            keys = list(eval(self.category_data['PRICE']).keys())
        else:
            keys = None
        return keys

    @property
    def is_solid(self):
        return self.category_data['solid']

    @property
    def can_append_data(self):
        flag = False
        record_num = len(self.value.split(','))
        if record_num < self.num_of_recipients:
            flag = True
        return flag


class VedomostFiller:
    def __init__(self, month, recipient=''):
        self.path_to_dir = f'months/{month}'
        self.path_to_mother_frame = f'{self.path_to_dir}/{month}.xlsx'

        # поле переменных для работы функций
        self.mother_frame = pd.DataFrame()
        self.prices = pd.DataFrame()
        self.r_vedomost = pd.DataFrame()

        self.day_row = cl.MonthData()
        self.day_row_index = None
        self.recipient = recipient
        self.r_filling_ser = pd.Series()
        self.non_filled_categories = []

        self.filling_now_cell = None

    @property
    def admin(self):
        return True if self.recipient == 'Egr' else False

    @property
    def r_name(self):
        return self.recipient

    @r_name.setter
    def r_name(self, name):
        self.recipient = name

    def get_mother_frame_and_prices(self):
        pass

    def get_mother_frame_and_refresh_values(self):
        md = cl.MonthData(self.path_to_mother_frame)
        self.prices = md.get_price_frame()
        self.mother_frame = md.load_and_prepare_vedomost()

        self.r_vedomost = md.limiting('for filling', self.r_name)

        # подумай над рефрешем

        if not self.day_row.vedomost.empty:
            self.day_row.vedomost = pd.DataFrame()
            self.day_row_index = None
            self.r_filling_ser = pd.Series()

        return (self.mother_frame,
                self.day_row,
                self.r_filling_ser)

    @property
    def days_for_filling(self):
        days_in_str_ser = self.r_vedomost['DATE'].map(lambda d: datetime.date.strftime(d, '%d.%m.%y')).to_dict()
        return {days_in_str_ser[i]: i for i in days_in_str_ser}

    def change_the_day_row(self, date_form_tg):
        self.day_row_index = self.days_for_filling[date_form_tg]
        self.day_row.vedomost = self.r_vedomost.loc[self.day_row_index:self.day_row_index]
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
        non_filled = self.r_filling_ser.to_dict()
        for cat in non_filled:
            if pd.notna(non_filled[cat]): # проверка на запись
                cell.cat_name, cell.cat_value = cat, non_filled[cat]
                if not cell.is_solid:
                    if not cell.can_append_data: # проверка на невозможность дописывания в яйчейку
                        del non_filled[cat]
                else:
                    del non_filled[cat]
        self.non_filled_categories = non_filled
        return self.non_filled_categories

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
        return self.filling_now_cell

    def fill_the_cell(self, new_value):
        if new_value == 'не мог':
            new_value = 'can`t'
        elif new_value == 'забыл':
            new_value = '!'

        if self.filling_now_cell.is_solid:
            if self.filling_now_cell.can_append_data:
                self.r_filling_ser.at[self.filling_now_cell.cat_name] = \
                    f'{self.filling_now_cell.cat_value},{self.r_name[0]}{new_value}'

            else:
                self.r_filling_ser.at[self.filling_now_cell.cat_name] = \
                    f'{self.r_name[0]}{new_value}'

        else:
            self.r_filling_ser.at[self.filling_now_cell] = new_value
        return self.filling_now_cell

    def save_day_data(self):
        for c in self.r_filling_ser.index:
            self.day_row.vedomost.loc[self.day_row_index, c] = self.r_filling_ser[c]

        self.mother_frame[self.day_row_index:self.day_row_index+1]\
            = self.day_row.vedomost

        if self.recipient_all_filled_flag:
            if pd.notna(self.mother_frame.at[self.day_row_index, 'DONE']):
                self.mother_frame.at[self.day_row_index, 'DONE'] = 'Y'
                # нужно потестить реакцию на DONE
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
    filler = VedomostFiller(month)

    filler.r_name = 'Egr'

    filler.get_mother_frame_and_refresh_values()
    cell = VedomostCell(filler.prices, num_of_recipietns=2)

    filler.change_the_day_row('17.10.23')
    filler.filtering_by_positions()
    filler.get_non_filled_categories()
    print(filler.non_filled_categories)
    cell.name = 'e:hygiene'
    filler.change_a_cell(cell)
    print(filler.filling_now_cell.cat_name, filler.filling_now_cell.cat_value)
    filler.fill_the_cell(new_value='9')
    print(filler.filling_now_cell.cat_name,
          filler.filling_now_cell.cat_value,
          'flgs',
          filler.filling_now_cell.is_solid,
          filler.filling_now_cell.can_append_data
          )
    print(filler.r_filling_ser)
    # filler.save_day_data()
#    print(filler.day_row.vedomost)
#    print(filler.mother_frame.loc[14:15])
#