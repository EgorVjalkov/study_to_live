import pandas as pd
import datetime
import classes as cl
from analytic_utilities import FrameForAnalyse
# сделал фильтрацию на уровне ведомостей, теперь каждых может заполнить то чтопо его рангу.
# Теперь нужно включать кнопочки с датами, добавить описание в каждую катеорию, о чем и как заполнять

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

    def get_rows_for_filling(self):
        day_rows_for_filling = self.get_r_vedomost().to_dict('index')
        for day_index in day_rows_for_filling:
            self.ff.items = day_rows_for_filling[day_index]
            self.ff.filtration([('nan', 'nan', 'pos')], behavior='row_values')
            if self.ff.items:
                self.day_rows_dict[day_index] = self.ff.items


filler = VedomostFiller(path, 'Lera')
filler.get_r_vedomost()
print(filler.vedomost)







