import pandas as pd
import datetime
import classes as cl
from analytic_utilities import FrameForAnalyse
# сделал фильтрацию на уровне ведомостей, теперь каждых может заполнить то чтопо его рангу.
# Теперь нужно включать кнопочки с датами, добавить описание в каждую катеорию, о чем и как заполнять
# важная тема с заполнением: неодходимо прописать как быть с многочленными категориями, типо мытья посуды или прогулок

MONTH = 'sep23'
recipients = ['Egr', 'Lera']

path = f'months/{MONTH}/{MONTH}.xlsx'


class VedomostFiller:
    def __init__(self, path_to_file, recipient):
        md = cl.MonthData(path_to_file)
        md.get_frames_for_working(limiting='for filling')

        self.vedomost = md.vedomost
        self.accessory = md.accessory
        self.categories = md.categories
        self.date = md.date
        self.prices = md.prices

        self.ff = FrameForAnalyse(df=self.vedomost)

        self.recipient = recipient

        self.day_rows_dict = {}

    @property
    def admin(self):
        return True if self.recipient == 'Egr' else False

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

    def get_cat_description(self, cat_name):
        return self.prices[cat_name].filter(items=['description', 'hint', 'type', 'solid'], axis=0)

    def fill_the_day_row(self, day_frame):
        row_index = day_frame.index.to_list()[0]
        for cat in day_frame.columns:
            mark = day_frame[cat].to_list()[0]
            if pd.isna(mark):
                cat_description = self.get_cat_description(cat)
                print(cat_description['description'])
                if cat_description['hint']:
                    print(cat_description['hint'])
                print()
                # здесь пока только тип заполняемого, именно тут интегрируется бот с его кнопками и т.д.
                day_frame.loc[row_index, cat] = cat_description['type']


filler = VedomostFiller(path, 'Lera')
filler.get_r_vedomost()
filler.fill_the_day_row(filler.vedomost[:1])
print(filler.vedomost)







