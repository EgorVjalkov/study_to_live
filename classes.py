import pandas as pd
from ComplexCondition import ComplexCondition
import numpy as np
import os

pd.set_option('display.max.columns', None)
#SHOW_COEF_CALC = False
class MonthData:
    def __init__(self, path, recipients):
        vedomost = pd.read_excel(path, sheet_name='vedomost').fillna(False)
        self.limit = len([i for i in vedomost['DONE'].to_list() if i])
        self.vedomost = vedomost[0:self.limit].fillna(0)
        self.prices = pd.read_excel(path, sheet_name='price', index_col=0).fillna(0)
        date_keys = ['DATE', 'DAY']
        self.accessory = self.vedomost.get([i for i in self.vedomost.columns if i == i.upper() and i not in date_keys])
        self.date = self.vedomost.get(date_keys)
        self.categories = self.vedomost.get([i for i in self.vedomost if i == i.lower()])
        meals_in = lambda i: 'meals' in i or 'diet' in i
        self.meals_columns = [i for i in self.categories.columns if meals_in(i)]
        self.NOT_meals_columns = [i for i in self.categories.columns if not meals_in(i)]
        self.recipients = {k: self.date for k in recipients}
        self.result_frame = {k: self.date.copy() for k in recipients}

    def get_named_vedomost(self, name):
        named_positions = [i[0] for i in self.recipients]
        for column in self.categories:
            position = column[0].upper()
            if [i for i in self.categories[column] if type(i) == str and i[0] in named_positions]:
                #print(24, column)
                column_list = [ComplexCondition(result=i).prepare_named_result(name) for i in self.categories[column]]
                #self.recipients[name] = self.recipients[name].join(pd.Series(self.categories[column], name=column))
                #self.recipients[name] = self.recipients[name].join(pd.Series(column_list, name=column+"named"))
                self.recipients[name] = self.recipients[name].join(pd.Series(column_list, name=column))
            else:
                if name[0] == position or position not in named_positions:
                    self.recipients[name] = self.recipients[name].join(self.categories[column])
        #print(self.recipients[name])
        return self.recipients

    def collect_to_result_frame(self, name, column_name, result_column):
        self.result_frame[name][column_name] = result_column
        return self.recipients

class AccessoryData:
    def __init__(self, af):
        self.af = af
        self.mods_frame = {}
        self.positions_logic = {
            'duty24': {'Lera': ['A', 'Z', 'H', 'L'], 'Egr': ['E']},
            'duty24, M': {'Lera': ['A', 'Z', 'L'], 'Egr': ['E']},
            'V': {'Lera': ['A', 'Z', 'L'], 'Egr': ['A', 'Z', 'E']},
            'M': {'Lera': ['A', 'Z', 'L'], 'Egr': ['E', 'H']},
            '': {'Lera': ['A', 'Z', 'H', 'L'], 'Egr': ['A', 'Z', 'H', 'E']}
        }

    def get_mods_frame(self):
        self.mods_frame = pd.DataFrame(index=self.af.index)
        self.mods_frame['zlata_mod'] = self.af['MOD']
        self.mods_frame['weak_mod'] = ['WEAK' + str(int(i)) if i else i for i in self.af['WEAK']]
        self.mods_frame['duty_mod'] = ['duty' + str(int(i)) if i else i for i in self.af['DUTY']]
        self.mods_frame['DIF_DUTY'] = [{'DIF_DUTY': str(int(i))} if i else i for i in self.af['DIF_DUTY']]
        #print(self.mods_frame[['duty', 'zlata']].eq('duty24', 'M')) #!!!!!!!!!!

        def f_recipient_mod(duty, zlata):
            if zlata == 'M' or duty == 'duty24':
                return ['Lera']
            else:
                return ['Egr', 'Lera']
        self.mods_frame['recipient_who_coef'] = list(map(f_recipient_mod,
                                                         self.mods_frame['duty_mod'],
                                                         self.mods_frame['zlata_mod']))

        def f_for_positions(*mods):
            #print(mods)
            mods_key = ', '.join([i for i in mods if i])
            if mods_key not in self.positions_logic:
                if 'duty24' in mods_key:
                    mods_key = 'duty24'
                else:
                    mods_key = ''
            #print(mods_key)
            return self.positions_logic[mods_key]
        self.mods_frame['positions'] = list(map(f_for_positions,
                                                self.mods_frame['duty_mod'],
                                                self.mods_frame['zlata_mod']))


class CategoryData:
    def __init__(self, active_recipient, cf, mf, pf, date_frame=''):
        self.active_recipient = active_recipient
        self.name = cf.name
        self.cat_frame = pd.DataFrame([True if i == 'T' else i for i in cf], columns=[self.name])
        self.position = self.name[0].upper()
        self.price_frame = pf[self.name]
        self.mod_frame = mf
        self.named_coefficients = {'Egr': 'DIF_DUTY'}


    def find_a_price(self, duty, result, positions):
        #print(positions)
        if self.position not in positions:
            return {'price': 0, 'price_calc': 'not in positions'}

        price_calc = {True: self.price_frame['True'], False: self.price_frame['False'], 'zero': 0}
        if duty:
            price_calc['duty'] = duty
            price_calc[False] = self.price_frame['dutyFalse']
            price_calc[True] = self.price_frame['dutyTrue']
        #print(self.name)
        #print(result, type(result), price_calc[True])
        if result:
            if result != 'zero' and type(price_calc[True]) == str:
                price = ComplexCondition(result, price_calc[True]).get_price()
            else:
                price = price_calc[result]
        else:
            price = price_calc[result]
        #print(price)

        return {'price': price, 'price_calc': price_calc}

    def add_price_column(self, show_calculation=False):
        named_positions = self.mod_frame['positions'].map(lambda i: i[self.active_recipient])
        price_list = list(map(self.find_a_price,
                              self.mod_frame['duty_mod'],
                              self.cat_frame[self.name],
                              named_positions))
        self.cat_frame['price'] = [i.pop('price') for i in price_list]
        if show_calculation:
            price_list = [list(i.values())[0] for i in price_list]
            self.cat_frame.insert(self.cat_frame.columns.get_loc('price'), 'price_calc', price_list)
            self.cat_frame.insert(self.cat_frame.columns.get_loc('price'), 'named_positions', named_positions)
            print(self.cat_frame)
            #print(self.mod_frame[['zlata_mod', 'duty_mod', 'positions']])
        return self.cat_frame

    def count_a_modification(self, *mods):
        mods = [i for i in mods if i]
        #print(mods)
        coefficient_dict = {}
        for i in mods:
            if type(i) == dict:
                i = mods.pop(mods.index(i))
                key, value = list(i)[0], i[list(i)[0]]
                i = eval(self.price_frame[key])[value] if type(self.price_frame[key]) == str else self.price_frame[key]
                coefficient_dict[key] = i
        positions = mods.pop(-1)
        who_coef_list = mods.pop(-1)
        #print(mods)
        if self.position in positions and self.active_recipient in who_coef_list:
            coefficient_dict.update({i: self.price_frame[i] if i in self.price_frame else 1 for i in mods})
        #if not SHOW_COEF_CALC:
        #    coefficient_dict = {k: coefficient_dict[k] for k in coefficient_dict if coefficient_dict[k] != 1}
        coefficient_dict['coef'] = np.array(list(coefficient_dict.values())).prod()
        #print(coefficient_dict)
        return coefficient_dict

    def total_count(self, price, coef):
        if price > 0:
            price *= coef
        return price

    def add_coef_and_result_column(self, show_calculation=False):
        self.cat_frame['positions'] = self.mod_frame['positions'].map(lambda e: e[self.active_recipient])
        print(self.cat_frame['positions'])
        mods = [self.mod_frame.to_dict('list')[i] for i in self.mod_frame.to_dict('list') if 'mod' in i]
        if self.active_recipient in self.named_coefficients:
            mods.append(self.mod_frame[self.named_coefficients[self.active_recipient]].to_list())
        mods.append(self.mod_frame['recipient_who_coef'].to_list())
        mods.append(self.cat_frame['positions'].to_list())
        coefs_list = list(map(self.count_a_modification, *mods))
        self.cat_frame['coef'] = [i.pop('coef') for i in coefs_list]
        self.cat_frame['result'] = list(map(self.total_count, self.cat_frame['price'], self.cat_frame['coef']))
        if show_calculation:
            self.cat_frame.insert(self.cat_frame.columns.get_loc('coef'), 'who_coef', self.mod_frame['recipient_who_coef'])
            self.cat_frame.insert(self.cat_frame.columns.get_loc('coef'), 'coef_count', coefs_list)
            print(self.cat_frame)
        return self.price_frame
