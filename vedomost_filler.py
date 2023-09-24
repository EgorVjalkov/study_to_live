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
        return self.prices[cat_name].filter(items=['description', 'hint', 'type', 'solid'], axis=0)

    def get_dates_for_filling(self):
        days_for_filling = self.vedomost['DATE'].to_list()
        days_for_filling = {datetime.date.strftime(i, '%d.%m.%y'): i for i in days_for_filling}
        return days_for_filling

    def change_the_day_row(self, date):
        self.ff.items = self.vedomost['DATE'].to_dict()
        self.ff.filtration([('=', date, 'pos')], behavior='index_values')
        day_frame = self.ff.present_by_items(self.vedomost)
        return day_frame

    #def fill_the_cell(self):
    #    for cell in self.day_frame:
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
    month = 'sep23'
    path = f'months/{month}/{month}.xlsx'
    filler = VedomostFiller(path, 'Lera')
    li = filler.get_dates_for_filling()








