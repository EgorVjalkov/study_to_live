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
    def count_a_month_sum(self, cat_sum, recipient):
        pass # stopped


class AccessoryData:
    def __init__(self, af):
        self.af = af
        self.mods_frame = {}

    def recipient_mod(self, duty, zlata):
        if duty == 'duty24' or zlata == 'M':
            return ['Lera']
        else:
            return ['Egr', 'Lera']

    def get_mods_frame(self):
        self.mods_frame = pd.DataFrame(index=self.af.index)
        self.mods_frame['zlata_mod'] = self.af['MOD']
        self.mods_frame['weak_mod'] = ['WEAK' + str(int(i)) if i else i for i in self.af['WEAK']]
        self.mods_frame['duty_mod'] = ['duty' + str(int(i)) if i else i for i in self.af['DUTY']]
        #print(self.mods_frame[['duty', 'zlata']].eq('duty24', 'M')) #!!!!!!!!!!
        self.mods_frame['recipient_who_coef'] = list(map(self.recipient_mod, self.mods_frame['duty_mod'], self.mods_frame['zlata_mod']))

        posit_f = lambda i: i == 'duty24' or i == 'M'
        for_position_frame = self.mods_frame[['duty_mod', 'zlata_mod']].applymap(posit_f)
        for_position_frame = zip(for_position_frame['duty_mod'], for_position_frame['zlata_mod'])
        positions = {
            (True, False): {'Lera': ['A', 'Z', 'F', 'L'], 'Egr': ['E']},
            (True, True): {'Lera': ['A', 'Z', 'F', 'L'], 'Egr': ['E']},
            (False, True): {'Lera': ['A', 'Z', 'L'], 'Egr': ['E', 'F']},
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

    def total_count(self, price, recipient_mod, coef, positions):
        # print(self.position, positions)
        if self.position not in positions:
            return 0
        elif self.position in positions and price <= 0:
            return price
        else:
            for recipient in self.recipients:
                if recipient in recipient_mod:
                    price *= coef
                    break
        return price

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
        #self.cat_frame['result'] = self.cat_frame['price'] * self.cat_frame['coef']
        return self.price_frame

    def add_recipients_column(self, recipients=(), show_calculation=False):
        if not recipients:
            recipients = self.recipients
        for name in recipients:
            self.cat_frame[name+'_positions'] = self.mod_frame['positions'].map(lambda e: e[name])
            self.cat_frame[name+'_total'] = list(map(self.total_count,
                                                     self.cat_frame['price'],
                                                     self.mod_frame['recipient_who_coef'],
                                                     self.cat_frame['coef'],
                                                     self.cat_frame[name+'_positions']))
            if not show_calculation:
                del self.cat_frame[name+'_positions']
            return self.cat_frame


dec22 = MonthData('months/dec22test/dec22.xlsx')
ad = AccessoryData(dec22.accessory)
# print(dec22.categories)
# print(dec22.accessory)
ad.get_mods_frame()
for cat in dec22.categories:
# cat = 'L:DIET'
    cd = CategoryData(dec22.categories[cat], ad.mods_frame, dec22.prices)
    cd.add_price_column(show_calculation=False)
    cd.add_coef_column(show_calculation=False)
    cd.add_recipients_column(show_calculation=True)
    print(cd.cat_frame['Lera_total'].sum())
