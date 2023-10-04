import pandas as pd
import datetime
import classes as cl
from analytic_utilities import FrameForAnalyse
# сделал фильтрацию на уровне ведомостей, теперь каждых может заполнить то чтопо его рангу.
# Теперь нужно включать кнопочки с датами, добавить описание в каждую катеорию, о чем и как заполнять
# важная тема с заполнением: неодходимо прописать как быть с многочленными категориями, типо мытья посуды или прогулок


class VedomostFiller:
    def __init__(self, path_to_file, recipient=''):
        md = cl.MonthData(path_to_file)
        md.get_frames_for_working(limiting='for filling')

        self.vedomost = md.vedomost
        self.accessory = md.accessory
        self.categories = md.categories
        self.date = md.date
        self.prices = md.prices

        self.ff = FrameForAnalyse(df=self.vedomost)

        self.recipient = recipient

        self.days_for_filling = {}
        self.day_frame = pd.DataFrame()
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
        return self.day_frame

    def get_non_filled_categories(self):
        index = self.day_frame.index[0]
        self.ff.items = self.day_frame.to_dict('index')[index]
        self.ff.filtration([('nan', 'nan', 'pos')], behavior='row_values')
        self.non_filled_categories = list(self.ff.items)
        return self.non_filled_categories

    #        mark = self.day_frame[cell].to_list()[0]
    #        if pd.isna(mark):
    #            print(mark)
    #            pass
    #            cat_description = self.get_cat_description(cat)
    #            #print(cat_description['description'])
    #            #if cat_description['hint']:
    #            #    print(cat_description['hint'])
    #            #print()
    #            # здесь пока только тип заполняемого, именно тут интегрируется бот с его кнопками и т.д.
    #            day_frame.loc[row_index, cat] = cat_description['type']
    #            # сделать нужно филлерчек


if __name__ == '__main__':
    print(1 // 4)
    month = 'oct23'
    path = f'months/{month}/{month}.xlsx'
    filler = VedomostFiller(path, 'Egr')
    li = filler.get_dates_for_filling()
    dddd = filler.get_cell_description('z:stroll')
    answer = [i for i in dddd[['description', 'hint']] if i]
    answer = '\n'.join(answer)
    print(answer)









