from collections import namedtuple

import numpy as np
import pandas as pd


Btn = namedtuple('Btn', 'text id')


class VedomostCell:
    def __init__(self, price_frame, recipient, name='', value=''):
        self.prices = price_frame
        self.recipient = recipient

        self.name = name
        self.old_value = value
        self.new_value = np.nan

    def __repr__(self):
        if self.already_filled:
            return f'Cell({self.name}, new: {self.new_value})'
        else:
            return f'Cell({self.name}, old: {self.old_value})'

    @property
    def btn(self):
        match pd.notna(self.old_value), pd.notna(self.new_value):
            case False, False:
                return Btn(f'{self.name}', f'{self.name}')
            case True, False:
                return Btn(f'{self.name}: {self.old_value}', f'{self.name}')
            case _, True:
                return Btn(f'{self.name}: {self.new_value}', f'{self.name}')

    @property
    def r_litera(self):
        return self.recipient[0]

    @property
    def new_cat_value(self):
        return self.new_value

    @new_cat_value.setter
    def new_cat_value(self, new_value):
        self.new_value = new_value

    @property
    def category_data(self):
        cat_data = self.prices[self.name]
        return cat_data

    @property
    def type(self):
        return self.category_data.loc['type']

    @property
    def description(self) -> str:
        descr_list = self.category_data.get(['description', 'hint', 'info']).to_list()
        descr_list = [e for e in descr_list if pd.notna(e)]
        if not descr_list:
            descr_list = ['Выберите вариант']
        return '\n'.join(descr_list)

    @property
    def keys(self):
        if 'range' in self.type:
            keys = list(eval(self.type))
            keys = [str(i) for i in keys]

        elif '[' in self.type:
            keys = eval(self.type)

        elif self.type == 'dict':
            keys = list(eval(self.category_data['PRICE']).keys())

        elif self.type == 'manual':
            keys = ['передать вручную']

        else:
            keys = []

        if pd.notna(self.category_data['add_keys']):
            keys.append(self.category_data['add_keys'])

        keys.extend(['не мог', 'забыл'])

        return keys

    @property
    def is_filled(self):
        return pd.notna(self.old_value)

    @property
    def has_private_value(self):
        return pd.notna(self.category_data['private_value'])

    @property
    def can_append_data(self):
        flag = False
        if self.is_filled and self.r_litera not in self.old_value:
            flag = True
        return flag

    @property
    def can_be_filled(self) -> bool:
        flag = False
        if self.is_filled:  # прoверка на заполненность
            if self.has_private_value: # проверка на возможность иметь несколько значение
                if self.can_append_data:  # проверка на возможность дописывания в яйчейку
                    flag = True
        else:
            flag = True
        return flag

    @property
    def can_be_corrected(self) -> bool:
        return not self.can_be_filled

    @property
    def already_filled(self):
        return pd.notna(self.new_value) and str(self.old_value) != str(self.new_value)

    def revert_value(self):
        revert_old_value = np.nan  # очистка ячейки в дефолте
        if self.is_filled and self.has_private_value:
            revert_old_value = [i for i in self.old_value.split(',')
                                if self.r_litera not in i]
            revert_old_value = ''.join(revert_old_value)
            print(revert_old_value)
        self.old_value = revert_old_value

    def print_description(self, acc_data=None):
        answer = self.description
        if not answer:
            answer = 'Нажмите кнопку на экране'
        else:
            if acc_data:
                answer.append(acc_data)
            answer = '\n'.join(answer)
        return answer

    def print_old_value_by(self, behavior: str):
        if behavior in ['correction', 'coefs']:
            answer = f'Принято. Предыдущие значение - "{self.old_value}"'
        else:
            answer = 'Принято'
        return answer

#a = np.nan
#print(pd.isna(a))
