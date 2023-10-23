import pandas as pd
import datetime
import classes as cl
from analytic_utilities import FrameForAnalyse
# важная тема с заполнением: неодходимо прописать как быть с многочленными категориями, типо мытья посуды или прогулок
# задроч с путем надо подумать как его слеоать!
# хрень с классом Сell


ff = FrameForAnalyse()


class Cell:
    def __init__(self, price_frame, name=''):
        self.prices = price_frame
        self.name = name
        self.value = None

    @property
    def cat_name(self):
        return self.name

    @cat_name.setter
    def cat_name(self, category_name):
        self.name = category_name

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
        self.filled = {}

        self.filling_now = None

    @property
    def admin(self):
        return True if self.recipient == 'Egr' else False

    @property
    def r_name(self):
        return self.recipient

    @r_name.setter
    def r_name(self, name):
        self.recipient = name

    def get_mother_frame_and_refresh_values(self):
        # здесь возможно облегчить суть, т.к. нет смысла кажды раз запускать например pricefr
        md = cl.MonthData(self.path_to_mother_frame)
        self.prices = md.get_price_frame()
        self.mother_frame = md.load_and_prepare_vedomost()

        self.r_vedomost = md.limiting('for filling', self.r_name)

        if not self.day_row.vedomost.empty:
            self.day_row.vedomost = pd.DataFrame()
            self.day_row_index = None
            self.r_filling_ser = pd.Series()
            self.filled.clear()

        return (self.mother_frame,
                self.day_row,
                self.r_filling_ser,
                self.filled)

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

    @property
    def non_filled_categories(self):
        non_filled = self.r_filling_ser.to_dict()
        non_filled = [i for i in non_filled if pd.isna(non_filled[i])]
        return non_filled

    def filtering_by_positions(self):
        if not self.day_row.vedomost.empty:
            filtered = [i for i in self.day_row.categories.columns
                        if i[0] in self.r_positions]
            self.r_filling_ser = self.day_row.categories.loc[self.day_row_index][filtered]
            print(self.r_filling_ser)
        return self.r_filling_ser

    @property
    def recipient_all_filled_flag(self):
        if not self.non_filled_categories:
            return True
        else:
            return False

    def change_a_cell(self, cat_name):
        self.filling_now = cat_name
        return self.filling_now

    def fill_the_cell(self, value):
        if value == 'не мог':
            value = 'can`t'
        elif value == 'забыл':
            value = '!'
        self.r_filling_ser.at[self.filling_now] = value

    def get_path_for_filled(self):
        date = self.mother_frame.date.loc[self.day_row_index, 'DATE']
        date = datetime.date.strftime(date, '%d_%m_%y')
        path = f'{self.path_to_dir}/{self.recipient}_{date}'
        return path

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
    filler.change_the_day_row('17.10.23')
    filler.filtering_by_positions()
    filler.change_a_cell('e:hygiene')
    print(filler.day_row.vedomost['DONE'])
    filler.fill_the_cell('9')
    print(filler.recipient_all_filled_flag)
    filler.save_day_data()
    print(filler.day_row.vedomost)
    print(filler.mother_frame.loc[14:15])
