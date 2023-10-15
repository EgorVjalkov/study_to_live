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
        self.day_frame_index = 0
        self.filled = {}
        self.all_filled_flag = False

    @property
    def admin(self):
        return True if self.recipient == 'Egr' else False

    @property
    def r_name(self):
        return self.recipient

    @r_name.setter
    def r_name(self, name):
        self.recipient = name

   # @property
   # def path(self):
   #     return self.path_to_dir

   # @path.setter
   # def path(self, new_path):
   #     self.path_to_dir = new_path

    @property
    def r_positions_ser(self):
        r = cl.Recipient(self.recipient, self.vedomost.date)
        #self.path = f'{self.path_to_dir}/{self.recipient}'
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
        return self.vedomost

    def change_the_day_row(self, date_form_tg):
        date = self.days_for_filling[date_form_tg]
        ff.items = self.vedomost.date['DATE'].to_dict()
        ff.filtration([('=', date, 'pos')], behavior='index_values')
        day_frame = ff.present_by_items(self.vedomost.categories)
        self.day_frame_index = list(ff.items)[0]
        day_positions = self.r_positions_ser.loc[self.day_frame_index]

        ff.items = list(day_frame.columns)
        ff.filtration([('positions', day_positions, 'pos')])
        self.day_categories_frame = ff.present_by_items(day_frame)
        return self.day_categories_frame

    def get_non_filled_categories(self):
        if not self.day_categories_frame.empty:
            ff.items = self.day_categories_frame.to_dict('index')[self.day_frame_index]
            ff.filtration([('nan', 'nan', 'pos')], behavior='row_values')
            self.non_filled_categories = list(ff.items)
        return self.non_filled_categories

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

            # зздесь нужно откровенный вопрос себе задать! как дальше жить!

    def is_day_filled(self):
        print(self.non_filled_categories)
        if not self.non_filled_categories:
            return self.all_filled_flag

    def save_day_data(self):
        for cat in self.filled:
            self.day_categories_frame.loc[self.day_frame_index, cat] = self.filled[cat]
        date = self.day_categories_frame.loc[self.day_frame_index, 'DATE']
        date = datetime.date.strftime(date, '%d_%m_%y')
        path = f'{self.path_to_dir}/{self.recipient}_{date}'
        if self.all_filled_flag:
            path = f'{path}_undone.xlsx'
        else:
            path = f'{path}_done.xlsx'
        print(path)

        self.day_categories_frame.to_excel(path, sheet_name=f'{date}')


if __name__ == '__main__':
    month = 'oct23'
    filler = VedomostFiller(month, 'Egr')
    filler.refresh_vedomost()
    print(filler.vedomost.prices)
    for i in filler.days_for_filling:
        filler.change_the_day_row(i)
        for cat in filler.non_filled_categories:
            pass


    #li = filler.get_dates_for_filling()
    #dddd = filler.get_cell_description('h:vacuum')
    #print(dddd['keys'])
