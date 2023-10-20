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
        self.day_row = cl.MonthData()
        self.recipient = recipient
        self.non_filled_categories = []
        self.filled = {}

    @property
    def admin(self):
        return True if self.recipient == 'Egr' else False

    @property
    def r_name(self):
        return self.recipient

    @r_name.setter
    def r_name(self, name):
        self.recipient = name

    @property
    def days_for_filling(self):
        days_for_filling = self.mother_frame.date['DATE'].to_list()
        days_for_filling = {datetime.date.strftime(i, '%d.%m.%y'): i for i in days_for_filling}
        return days_for_filling

    def get_mother_frame_and_refresh_values(self):
        # здесь возможно облегчить суть, т.к. нет смысла кажды раз запускать например pricefr
        self.mother_frame = cl.MonthData(self.path_to_mother_frame)
        self.mother_frame.get_vedomost()
        self.mother_frame.get_price_frame()
        self.mother_frame.get_frames_for_working(limiting='for filling')

        if not self.day_row.vedomost.empty:
            self.day_row.vedomost = pd.DataFrame()
            self.non_filled_categories.clear()
            self.filled.clear()

        return (self.mother_frame,
                self.day_row,
                self.non_filled_categories,
                self.filled)

    @property
    def day_row_index(self):
        return self.day_row.date.index.to_list()[0]

    def change_the_day_row(self, date_form_tg):
        date = self.days_for_filling[date_form_tg]
        ff.items = self.mother_frame.date['DATE'].to_dict()
        ff.filtration([('=', date, 'pos')], behavior='index_values')
        day_frame = ff.present_by_items(self.mother_frame.vedomost)

        self.day_row.vedomost = day_frame
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

    def get_non_filled_categories(self):
        if not self.day_row.vedomost.empty:
            ff.items = list(self.day_row.categories.columns)
            ff.filtration([('positions', self.r_positions, 'pos')])
            r_categories_frame = ff.present_by_items(self.day_row.categories)
            ff.items = r_categories_frame.to_dict('index')[self.day_row_index]
            ff.filtration([('nan', 'nan', 'pos')], behavior='row_values')
            self.non_filled_categories = list(ff.items)
        return self.non_filled_categories

    @property
    def all_filled_flag(self):
        if not self.non_filled_categories:
            return True
        else:
            return False

    def add_a_cell(self, cat_name):
        # аопрос а нужен ли вообще ыелфюфиллев, может сразу писать в дэйроу
        self.filled[cat_name] = None

    def fill_a_cell(self, value):
        for cat_name in self.filled:
            if not self.filled[cat_name]:
                if value == 'не мог':
                    value = 'can`t'
                elif value == 'забыл':
                    value = '!'
                self.filled[cat_name] = value
                return cat_name

    def get_path_for_filled(self):
        date = self.mother_frame.date.loc[self.day_row_index, 'DATE']
        date = datetime.date.strftime(date, '%d_%m_%y')
        path = f'{self.path_to_dir}/{self.recipient}_{date}'
        return path

    def save_day_data(self):
        for c in self.filled:
            self.day_row.vedomost.loc[self.day_row_index, c] = self.filled[c]

        self.mother_frame.vedomost.loc[self.day_row_index:self.day_row_index+1]\
            = self.day_row.vedomost
        print(self.mother_frame.vedomost)

        if self.all_filled_flag:
            if pd.isna(self.mother_frame.vedomost.at[self.day_row_index, 'DONE']):
                self.mother_frame.vedomost.at[self.day_row_index, 'DONE'] = 'Y'
                # нужно потестить реакцию на DONE
            else:
                self.mother_frame.vedomost.at[self.day_row_index, 'DONE'] = self.recipient[0]

# здеся тестинг записи на странице (нью, реплайс или оверлэй)
        with pd.ExcelWriter(
                self.path_to_mother_frame,
                mode='a',
                engine='openpyxl',
                if_sheet_exists='new'
        ) as mf_writer:
            self.mother_frame.to_excel(mf_writer, sheet_name='vedomost')


if __name__ == '__main__':
    month = 'oct23'
    filler = VedomostFiller(month, 'Egr')
    filler.get_mother_frame_and_refresh_values()
    filler.change_the_day_row('15.10.23')
    filler.get_non_filled_categories()
    print(filler.non_filled_categories)
    print(filler.mother_frame.vedomost.loc[filler.day_row_index].at['DONE'])


    #li = filler.get_dates_for_filling()
    #dddd = filler.get_cell_description('h:vacuum')
    #print(dddd['keys'])
