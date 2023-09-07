import pandas as pd
import datetime
import classes as cl
from analytic_utilities import FrameForAnalyse
# сделай возможеость заполнять логику только для себя, остальное позволь заполнять жене
# сейчас нужно опрелеиться с правали на заполнение категорий

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

        self.recipient = recipient

        self.day_rows_dict = {}

    @property
    def admin(self):
        return True if self.recipient == 'Egr' else False

    @property
    #
    def r_positions(self):
        r = cl.Recipient(self.recipient, self.date)
        r.positions.append(r.private_position)
        return r.positions

    def get_recipient_rules(self):
        if not self.admin:
            self.columns_for_filling = []

    def get_rows_for_filling(self):
        ff = FrameForAnalyse(df=self.vedomost)
        day_rows_for_filling = ff.df.to_dict('index')
        for day_index in day_rows_for_filling:
            ff.items = day_rows_for_filling[day_index]
            ff.filtration([('nan', 'nan', 'pos')], behavior='row_values')
            # можно бы тут подумать как сократить эти строки и улучшить свою ф фильтрации
            ff.items = list(ff.items.keys())
            ff.filtration([('positions', self.r_positions, 'pos')], behavior='columns')
            if ff.items:
                self.day_rows_dict[day_index] = ff.items


filler = VedomostFiller(path, 'Egr')
filler.get_rows_for_filling()
print(filler.r_positions)
print(filler.day_rows_dict)







