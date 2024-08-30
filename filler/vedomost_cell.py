import datetime
from collections import namedtuple
from dataclasses import dataclass
from typing import Optional

import pandas as pd

from filler.date_funcs import today_for_filling

Btn = namedtuple('Btn', 'text id')


@dataclass
class VedomostCell:
    name: str
    current_value: Optional[str]
    recipient: str
    category_data: pd.Series
    new_value: Optional[str] = None

    def __repr__(self):
        if self.new_v:
            return f'Cell({self.name}, v: {self.new_v})'
        else:
            return f'Cell({self.name}, v: {self.current_v})'

    @property
    def btn(self):
        match bool(self.current_value), bool(self.new_value):
            case _, True:
                return Btn(f'{self.name}: {self.new_value}', f'{self.name}')
            case True, False:
                return Btn(f'{self.name}: {self.current_value}', f'{self.name}')
            case False, _:
                return Btn(f'{self.name}', f'{self.name}')

    @property
    def r_litera(self):
        return self.recipient[0]

    @property
    def current_v(self):
        return self.current_value

    @current_v.setter
    def current_v(self, new_value: str):
        self.current_value = new_value

    @property
    def new_v(self):
        return self.new_value

    @new_v.setter
    def new_v(self, new_value: str):
        self.new_value = new_value

    @property
    def type(self):
        return self.category_data.loc['type']

    @property
    def description(self) -> str:
        descr_list = self.category_data.get(['description', 'hint', 'info']).to_list()
        descr_list = [e for e in descr_list if e]
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

        if self.category_data['add_keys']:
            keys.append(self.category_data['add_keys'])

        if behavior != 'coefs':
            keys.extend(['не мог', 'забыл'])

        return keys

    @property
    def is_filled(self):
        return bool(self.current_v)

    @property
    def already_filled(self):
        return bool(self.new_v)

    @property
    def has_many_values(self) -> bool:
        return bool(self.category_data['private_value'])

    @property
    def can_append_data(self) -> bool:
        match self.is_filled, self.r_litera:
            case True, r_litera if r_litera not in self.current_v:
                return True
        return False

    @property
    def can_be_filled(self) -> bool:
        #print(self.is_filled, self.has_many_values, self.can_append_data)
        match self.is_filled, self.has_many_values, self.can_append_data:
            case False, _, _:
                return True
            case True, True, True:
                return True
        return False

    @property
    def can_be_corrected(self) -> bool:
        return not self.can_be_filled

    def fill(self, value: str) -> object:
        print('filled?', self.is_filled)
        match self.is_filled, self.has_many_values, self.can_append_data:
            case True, True, True:
                self.new_v = f'{self.current_v},{self.recipient[0]}{value}' # сложное в заплненную
            case True, True, False:
                self.clear_r_value()
                self.fill(value) # значение сбрасывается и клетка снова запускается в запись
            case True, False, _:
                self.new_v = value # простое со сбросом
            case False, True, _:
                self.new_v = f'{self.recipient[0]}{value}' # именное в пустую
            case False, False, _:
                self.new_v = value # простое в пустую
        return self

    def clear_r_value(self) -> object:
        values_list = self.current_v.split(',')
        filtered_values_by_recipient = [i for i in values_list if i[0] != self.r_litera]
        if filtered_values_by_recipient:
            self.current_v = ','.join(filtered_values_by_recipient)
        else:
            self.current_v = None
        print('cleared', self.current_v)
        return self

    def print_current_value(self):
        if self.current_value:
            answer = f'Принято. Предыдущие значение - "{self.current_value}"'
        else:
            answer = 'Принято'
        return answer
