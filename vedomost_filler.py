import pandas as pd
import datetime
import classes as cl
from analytic_utilities import FrameForAnalyse
# сделал фильтрацию на уровне ведомостей, теперь каждых может заполнить то чтопо его рангу.
# Теперь нужно включать кнопочки с датами, добавить описание в каждую катеорию, о чем и как заполнять
# важная тема с заполнением: неодходимо прописать как быть с многочленными категориями, типо мытья посуды или прогулок


class VedomostFiller:
    def __init__(self, month, recipient=''):
        path_to_dir = f'months/{month}/'
        md = cl.MonthData(path=f'{path_to_dir}/{month}.xlsx')
        md.get_frames_for_working(limiting='for filling')

        self.path_to_filled = f'{path_to_dir}/filled_by_bot.xlsx'

        self.vedomost = md.vedomost
        self.accessory = md.accessory
        self.categories = md.categories
        self.date = md.date
        self.prices = md.prices

        self.ff = FrameForAnalyse(df=self.vedomost)

        self.recipient = recipient

        self.days_for_filling = {}
        self.day_frame = pd.DataFrame()
        self.day_frame_index = 0
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

    def get_r_vedomost(self):
        r = cl.Recipient(self.recipient, self.date)
        r.positions.append(r.private_position)
        self.ff.items = list(self.categories.columns)
        self.ff.filtration([('positions', r.positions, 'pos')])
        self.categories = self.ff.present_by_items(self.categories)
        if self.admin:
            self.vedomost = pd.concat([self.date, self.accessory, self.categories], axis=1)
        else:
            self.vedomost = pd.concat([self.date, self.categories], axis=1)
        return self.vedomost

    def get_cell_description(self, cat_name):
        cat_data = self.prices[cat_name]
        description = cat_data.filter(items=['description', 'hint', 'type', 'solid'], axis=0)
        if 'range' in description['type']:
            description['keys'] = eval(description['type'])
            print(description['keys'])
        elif description['type'] == 'dict':
            description['keys'] = list(eval(cat_data['PRICE']).keys())
        return description

    def get_dates_for_filling(self):
        days_for_filling = self.vedomost['DATE'].to_list()
        self.days_for_filling = {datetime.date.strftime(i, '%d.%m.%y'): i for i in days_for_filling}
        return self.days_for_filling

    def change_the_day_row(self, date):
        self.ff.items = self.vedomost['DATE'].to_dict()
        self.ff.filtration([('=', date, 'pos')], behavior='index_values')
        self.day_frame = self.ff.present_by_items(self.vedomost)
        self.day_frame_index = self.day_frame.index[0]
        return self.day_frame

    def get_non_filled_categories(self):
        self.ff.items = self.day_frame.to_dict('index')[self.day_frame_index]
        self.ff.filtration([('nan', 'nan', 'pos')], behavior='row_values')
        self.non_filled_categories = list(self.ff.items)
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

    def is_day_filled(self):
        print(self.non_filled_categories)
        if self.non_filled_categories:
            return False
        else:
            return True

    def save_day_data(self):
        for cat in self.filled:
            self.vedomost.loc[self.day_frame_index, cat] = self.filled[cat]
        print(self.vedomost)
        #self.vedomost.to_excel(path=f'{self.path_to_filled})', sheet_name='vedomost')


if __name__ == '__main__':
    print(1 // 4)
    month = 'oct23'
    filler = VedomostFiller(month, 'Egr')
    li = filler.get_dates_for_filling()
    dddd = filler.get_cell_description('z:stroll')
    answer = [i for i in dddd[['description', 'hint']] if i]
    answer = '\n'.join(answer)
    print(answer)









