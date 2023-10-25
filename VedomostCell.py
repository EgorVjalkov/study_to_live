import numpy as np
import pandas as pd


class VedomostCell:
    def __init__(self, price_frame, num_of_recipietns, name=''):
        self.prices = price_frame
        self.name = name
        self.num_of_recipients = num_of_recipietns
        self.value = None

    @property
    def cat_name(self):
        return self.name

    @cat_name.setter
    def cat_name(self, category_name):
        self.name = category_name

    @property
    def cat_value(self):
        return self.value

    @cat_value.setter
    def cat_value(self, value):
        self.value = value

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

    @property
    def is_empty(self):
        return pd.isna(self.value)

    @property
    def has_private_value(self):
        return self.category_data['private_value']

    @property
    def can_append_data(self):
        flag = False
        record_num = len(self.value.split(','))
        if record_num < self.num_of_recipients:
            flag = True
        return flag

a = np.nan
print(pd.isna(a))