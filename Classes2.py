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
        self.mods_frame['zlata_mod'] = self.af['MOD']
        self.mods_frame['weak_mod'] = ['WEAK' + str(int(i)) if i else i for i in self.af['WEAK']]
        self.mods_frame['duty_mod'] = ['duty' + str(int(i)) if i else i for i in self.af['DUTY']]
        only_lera_mod_f = lambda i, e: i == 'duty24' or e == 'M'
        #print(self.mods_frame[['duty', 'zlata']].eq('duty24', 'M')) #!!!!!!!!!!
        only_lera_mod = list(map(only_lera_mod_f, self.mods_frame['duty_mod'], self.mods_frame['zlata_mod']))
        self.mods_frame['only_lera_coef'] = only_lera_mod

        posit_f = lambda i: i == 'duty24' or i == 'M'
        for_position_frame = self.mods_frame[['duty_mod', 'zlata_mod']].applymap(posit_f)
        for_position_frame = zip(for_position_frame['duty_mod'], for_position_frame['zlata_mod'])
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
        self.cat_frame = pd.DataFrame([True if i == 'T' else i for i in cf], columns=[self.name])
        self.position = self.name[0]
        self.price_frame = pf[self.name]
        self.mod_frame = mf
        self.recipients = ['Egr', 'Lera']
        #self.date_frame = date_frame

    def find_a_price(self, duty, result):
        price_calc = {True: self.price_frame['True'], False: self.price_frame['False']}
        if duty:
            price_calc['duty'] = duty
            price_calc[False] = self.price_frame['dutyFalse']
            price_calc[True] = self.price_frame['dutyTrue']

        if type(result) == bool:
            price = int(price_calc[result])
        else:
            price = ComplexCondition(result, price_calc[True]).get_price()

        return {'price': price, 'price_calc': price_calc}

    def count_a_modification(self, *args):
        mods = [i for i in args if i]
        coefficient_dict = {k: self.price_frame[k] for k in mods if k in self.price_frame}
        coefficient_dict['coef'] = np.array(list(coefficient_dict.values())).prod()

        return coefficient_dict

    def add_price_column(self, show_calculation=False):
        price_list = list(map(self.find_a_price, self.mod_frame['duty_mod'], self.cat_frame[self.name]))
        self.cat_frame['price'] = [i.pop('price') for i in price_list]
        if show_calculation:
            price_list = [list(i.values())[0] for i in price_list]
            self.cat_frame.insert(self.cat_frame.columns.get_loc('price'), 'price_calc', price_list)
        return self.cat_frame

    def add_coef_column(self, show_calculation=False):
        mods = [self.mod_frame.to_dict('list')[i] for i in self.mod_frame.to_dict('list') if 'mod' in i]
        coefs_list = list(map(self.count_a_modification, *mods))
        self.cat_frame['coef'] = [i.pop('coef') for i in coefs_list]
        if show_calculation:
            self.cat_frame.insert(self.cat_frame.columns.get_loc('coef'), 'coef_count', coefs_list)
        self.cat_frame['result'] = self.cat_frame['price'] * self.cat_frame['coef']
        return self.price_frame

    def add_recipients_column(self, recipients=''):
        pass



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
    cd.add_price_column(show_calculation=True)
    cd.add_coef_column(show_calculation=True)
    break
