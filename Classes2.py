import pandas as pd
from Classes import ComplexCondition
from random import choice, randint
import datetime
import numpy as np

pd.set_option('display.max.columns', None)

class MonthData:
    def __init__(self, path):
        vedomost = pd.read_excel(path, sheet_name='vedomost').fillna(False)
        self.days = len([i for i in vedomost['DATE'].to_list() if i])
        self.vedomost = vedomost[0:self.days].fillna(0)
        self.prices = pd.read_excel(path, sheet_name='price', index_col=0).fillna(0)
        accessory_keys = ['MOD', 'WEAK', 'DUTY']
        date_keys = ['DATE', 'DAY']
        self.accessory = self.vedomost.get(accessory_keys)
        self.date = self.vedomost.get(date_keys)
        category_keys = [i for i in self.vedomost if i not in (accessory_keys + date_keys)]
        self.categories = self.vedomost.get(category_keys)


class AccessoryData:
    def __init__(self, af):
        self.af = af
        self.mods_frame = {}

    def get_mods_frame(self):
        self.mods_frame = pd.DataFrame(index=self.af.index)
        self.mods_frame['zlata'] = self.af['MOD']
        self.mods_frame['weak'] = ['WEAK' + str(int(i)) if i else i for i in self.af['WEAK']]
        self.mods_frame['duty'] = ['duty' + str(int(i)) if i else i for i in self.af['DUTY']]
        only_lera_mod_f = lambda i, e: i == 'duty24' or e == 'M'
        #print(self.mods_frame[['duty', 'zlata']].eq('duty24', 'M')) #!!!!!!!!!!
        only_lera_mod = list(map(only_lera_mod_f, self.mods_frame['duty'], self.mods_frame['zlata']))
        self.mods_frame['only lera mod'] = only_lera_mod

        posit_f = lambda i: i == 'duty24' or i == 'M'
        for_position_frame = self.mods_frame[['duty', 'zlata']].applymap(posit_f)
        for_position_frame = zip(for_position_frame['duty'], for_position_frame['zlata'])
        positions = {
            (True, False): {'Lera': ['A', 'L', 'Z'], 'Egr': ['E']},
            (True, True): {'Lera': ['A', 'L', 'Z'], 'Egr': ['E']},
            (False, True): {'Lera': ['A', 'L', 'Z'], 'Egr': ['E', 'F']},
            (False, False): {'Lera': ['A', 'Z', 'F', 'L'], 'Egr': ['A', 'Z', 'F', 'E']}
        }
        self.mods_frame['positions'] = [positions[i] for i in list(for_position_frame)]

        return self.mods_frame


class CategoryData:
    def __init__(self, cf, mf, pf, date_frame=''):
        self.name = cf.name
        if cf.dtypes == 'float':
            cf.astype('int')
        self.cat_frame = pd.Series([True if i == 'T' else i for i in cf], name=self.name)
        self.position = self.name[0]
        self.price_frame = pf[self.name]
        self.mod_frame = mf
        self.recipients = ['Egr', 'Lera']
        #self.date_frame = date_frame

    def find_a_price(self, duty, result):
        cell_price = {True: self.price_frame['True'], False: self.price_frame['False']}
        if duty:
            cell_price[False] = self.price_frame['duty_False']
            cell_price[True] = self.price_frame['duty_24']

        if type(result) == bool:
            cell_price = int(cell_price[result])
        else:
            cell_price = ComplexCondition(result, cell_price[True]).get_price()

        return cell_price
    def add_price_column(self):
        print(self.cat_frame)
        prices = list(map(self.find_a_price, self.mod_frame['duty'], self.cat_frame))
        print(prices)

        # if self.duty24:
        #
        #     self.only_lera_mod = True
        # else:
        #     self.positions = {'Lera': ['L'], 'Egr': ['E'], 'All': ['A', 'Z', 'F']}
        #     self.only_lera_mod = False
        # for k in self.positions:
        #     if self.first_char in self.positions[k]:
        #         self.recipient = k
        #
        # return self.mods_frame





        # for i in self.af:
        #     mods_dict[i] = self.accessory[i].to_dict()[result_key]
        #
        # self.zlata_mod = mods_dict['MOD']
        # self.weak_child_mod = mods_dict['WEAK']
        # self.volkhov_alone_mod = True if mods_dict['MOD'] == 'M' else False
        # self.on_duty = True if mods_dict['DUTY'] or self.volkhov_alone_mod else False
        # self.duty24 = True if mods_dict['DUTY'] == 24 or self.volkhov_alone_mod else False
        # self.duty_day = True if mods_dict['DUTY'] == 8 else False
        # collections
dec22 = MonthData('months/dec22test/dec22.xlsx')
ad = AccessoryData(dec22.accessory)
# print(dec22.categories)
# print(dec22.accessory)
ad.get_mods_frame()
for cat in dec22.categories:
    cd = CategoryData(dec22.categories[cat], ad.mods_frame, dec22.prices)
    cd.add_price_column()
    break
