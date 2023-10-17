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
        self.path_to_vedomost = f'{self.path_to_dir}/{month}.xlsx'

        # поле переменных для работы функций
        self.vedomost = pd.DataFrame()
        self.recipient = recipient
        self.day_categories_frame = pd.DataFrame()
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
    def r_positions_ser(self):
        r = cl.Recipient(self.recipient, self.vedomost.date)
        r.get_and_collect_r_name_col(self.vedomost.accessory['COM'], 'children')
        r.get_and_collect_r_name_col(self.vedomost.accessory['PLACE'], 'place')
        r.get_and_collect_r_name_col(self.vedomost.accessory['DUTY'], 'duty')
        r.get_family_col()
        r.get_r_positions_col()
        return r.mod_data['positions']

    @property
    def days_for_filling(self):
        days_for_filling = self.vedomost.date['DATE'].to_list()
        days_for_filling = {datetime.date.strftime(i, '%d.%m.%y'): i for i in days_for_filling}
        return days_for_filling

    def refresh_vedomost(self):
        self.vedomost = cl.MonthData(self.path_to_vedomost)
        self.vedomost.get_frames_for_working(limiting='for filling')
        self.day_categories_frame = pd.DataFrame()
        self.non_filled_categories = {}
        self.filled = {}
        return self.vedomost

    @property
    def day_frame_index(self):
        return self.day_categories_frame.index.to_list()[0]

    def change_the_day_row(self, date_form_tg):
        date = self.days_for_filling[date_form_tg]
        ff.items = self.vedomost.date['DATE'].to_dict()
        ff.filtration([('=', date, 'pos')], behavior='index_values')
        self.day_categories_frame = ff.present_by_items(self.vedomost.categories)
        return self.day_categories_frame

    def get_non_filled_categories(self):
        if not self.day_categories_frame.empty:
            day_positions = self.r_positions_ser.loc[self.day_frame_index]
            ff.items = list(self.day_categories_frame.columns)
            ff.filtration([('positions', day_positions, 'pos')])
            r_categories_frame = ff.present_by_items(self.day_categories_frame)
            ff.items = r_categories_frame.to_dict('index')[self.day_frame_index]
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
        date = self.vedomost.date.loc[self.day_frame_index, 'DATE']
        date = datetime.date.strftime(date, '%d_%m_%y')
        path = f'{self.path_to_dir}/{self.recipient}_{date}'
        return path

    def save_day_data(self):
        for c in self.filled:
            self.vedomost.loc[self.day_frame_index, c] = self.filled[c]
        # тут есть идея все писать срузц в ведомость и в графе доне ставить E L или Y
        path = self.get_path_for_filled()
        if self.all_filled_flag:
            pass
        else:
            path = f'{path}.csv'
        print(path)
        self.day_categories_frame.to_csv(path)
        #with open(path, 'w') as file:
        #
        #    csv.writer()


if __name__ == '__main__':
    month = 'oct23'
    filler = VedomostFiller(month, 'Egr')
    filler.refresh_vedomost()
    filler.change_the_day_row('15.10.23')
    filler.get_non_filled_categories()


    #li = filler.get_dates_for_filling()
    #dddd = filler.get_cell_description('h:vacuum')
    #print(dddd['keys'])
