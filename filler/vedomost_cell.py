import datetime
from collections import namedtuple
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd

from filler.date_funcs import today_for_filling

Btn = namedtuple('Btn', 'text id')


@dataclass
class VedomostCell:
    name: str
    current_value: str
    recipient: str
    category_data: pd.Series
    new_value: Optional[str] = None

    def __repr__(self):
        if self.already_filled:
            return f'Cell({self.name}, new: {self.new_value})'
        else:
            return f'Cell({self.name}, old: {self.current_value})'

    @property
    def btn(self):
        match pd.notna(self.current_value), pd.notna(self.new_value):
            case False, False:
                return Btn(f'{self.name}', f'{self.name}')
            case True, False:
                return Btn(f'{self.name}: {self.current_value}', f'{self.name}')
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
    def type(self):
        return self.category_data.loc['type']

    @property
    def description(self) -> str:
        descr_list = self.category_data.get(['description', 'hint', 'info']).to_list()
        descr_list = [e for e in descr_list if pd.notna(e)]
        if not descr_list:
            descr_list = ['Выберите вариант']
        return '\n'.join(descr_list)

    def get_keys(self, behavior: str, date: datetime.date):
        keys = []
        match self.type:
            case t if 'range' in t:
                keys = [str(i) for i in (eval(t))]

            case 'dict':
                keys = list(eval(self.category_data['PRICE']).keys())

            case 'time':
                if date == today_for_filling():
                    keys = ['сейчас!']

            case 'manual':
                keys = ['вручную']

            case t:
                keys = eval(t)

        if pd.notna(self.category_data['add_keys']):
            keys.append(self.category_data['add_keys'])

        if behavior != 'coefs':
            keys.extend(['не мог', 'забыл'])

        return keys

    @property
    def is_filled(self):
        return bool(self.current_value)

    @property
    def already_filled(self):
        return bool(self.new_value)

    @property
    def has_private_value(self):
        return pd.notna(self.category_data['private_value'])

    @property
    def can_append_data(self):
        flag = False
        if self.is_filled and self.r_litera not in self.current_value:
            flag = True
        return flag

    @property
    def can_be_filled(self) -> bool:
        flag = False
        if self.is_filled:  # прoверка на заполненность
            if self.has_private_value:  # проверка на возможность иметь несколько значение
                if self.can_append_data:  # проверка на возможность дописывания в яйчейку
                    flag = True
        else:
            flag = True
        return flag

    @property
    def can_be_corrected(self) -> bool:
        return not self.can_be_filled

    def fill(self, value: str) -> object:
        print(self.is_filled)
        if self.is_filled:
            self.new_cat_value = f'{self.current_value},{self.recipient[0]}{value}'

        else:
            if self.has_private_value:
                self.new_cat_value = f'{self.recipient[0]}{value}'
            else:
                self.new_cat_value = value
        return self

    def revert(self) -> object:
        reverted_old_value = None  # очистка ячейки в дефолте
        if self.is_filled and self.has_private_value:
            print(self.current_value)
            values_list = self.current_value.split(',')
            print(values_list)
            filtered_values_list = [i for i in values_list if i[0] != self.r_litera]
            print(filtered_values_list)
            reverted_old_value = ','.join(values_list)
        self.current_value = reverted_old_value
        return self

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
            answer = f'Принято. Предыдущие значение - "{self.current_value}"'
        else:
            answer = 'Принято'
        return answer

#a = np.nan
#print(pd.isna(a))
