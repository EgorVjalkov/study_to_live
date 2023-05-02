import pandas as pd
from ComplexCondition import ComplexCondition
import numpy as np
pd.set_option('display.max.columns', None)


class MonthData:
    def __init__(self, path, recipients):
        vedomost = pd.read_excel(path, sheet_name='vedomost').fillna(False)
        self.limit = len([i for i in vedomost['DONE'].to_list() if i])
        self.vedomost = vedomost[0:self.limit]
        self.prices = pd.read_excel(path, sheet_name='price', index_col=0).fillna(0)
        date_keys = ['DATE', 'DAY']
        self.accessory = self.vedomost.get([i for i in self.vedomost.columns if i == i.upper() and i not in date_keys])
        self.date = self.vedomost.get(date_keys)
        self.categories = self.vedomost.get([i for i in self.vedomost if i == i.lower()])
        meals_is = lambda i: 'meals' in i or 'diet' in i
        self.meals_columns = [i for i in self.categories.columns if meals_is(i)]
        self.NOT_meals_columns = [i for i in self.categories.columns if not meals_is(i)]
        self.recipients = {k: self.date.copy() for k in recipients}

        date_frame_for_result_frame = self.date.copy().astype('str').set_index('DATE')
        date_frame_for_result_frame = pd.concat(
            [date_frame_for_result_frame, pd.DataFrame(['count', 'sum'], columns=date_frame_for_result_frame.columns)]
        )
        self.result_frame = {k: date_frame_for_result_frame for k in recipients}
        print(self.result_frame)

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

    def get_result_column(self, column_name, result_column, true_count):
        result = round(result_column.sum(), 2)
        result_column = result_column.to_list()
        result_column.append(true_count)
        result_column.append(result)
        result_column = pd.Series(result_column, name=column_name)
        return result_column

    def collect_to_result_frame(self, name, column_name, result_column, true_count):
        #print(self.result_frame[name])
        new_column = self.get_result_column(column_name, result_column, true_count)
        self.result_frame[name] = pd.concat([self.result_frame[name], new_column], axis=1)
        print(self.result_frame[name])

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
        self.children_positions = ('A', 'Z')
        self.named_coefficients = {'Egr': ['DIF_DUTY'], 'Lera': []}

    def get_mods_frame(self):
        self.mods_frame = pd.DataFrame(index=self.af.index)
        self.mods_frame['duty'] = ['duty' + str(int(i)) if i else i for i in self.af['DUTY']]
        self.mods_frame['zlata_mod'] = self.af['MOD']
        self.mods_frame['weak_mod'] = ['WEAK' + str(int(i)) if i else i for i in self.af['WEAK']]
        self.mods_frame['DIF_DUTY'] = [{'DIF_DUTY': str(int(i))} if i else i for i in self.af['DIF_DUTY']]

        def f_for_positions(*mods):
            #print(mods)
            mods = ['' if i == 'duty8' else i for i in mods]
            mods_key = ', '.join([i for i in mods if i])
            if mods_key not in self.positions_logic:
                if 'duty24' in mods_key:
                    mods_key = 'duty24'
                else:
                    mods_key = ''
            #print(mods_key)
            return self.positions_logic[mods_key]
        self.mods_frame['positions'] = list(map(f_for_positions,
                                                self.mods_frame['duty'],
                                                self.mods_frame['zlata_mod']))

        def with_children(positions):
            recipient_list = []
            for r in positions:
                pos = [i for i in positions[r] if i in self.children_positions]
                if pos:
                    recipient_list.append(r)
            return recipient_list
        self.mods_frame['with_children'] = list(map(with_children, self.mods_frame['positions']))

        mods_for_coef = self.mods_frame.get([i for i in self.mods_frame.columns if 'mod' in i])
        mods_for_coef = mods_for_coef.to_dict('index')
        all_named_mods = []
        x = [all_named_mods.extend(i) for i in self.named_coefficients.values()]
        named_mods = self.mods_frame.get(all_named_mods).to_dict('index')

        def named_coefs(positions, duty, with_children, coef_dict, named_coefs):
            new_coef_dict = {k: coef_dict.copy() for k in list(positions.keys())}
            for r in new_coef_dict:
                if r not in with_children:
                    if duty == 'duty24':
                        new_coef_dict[r].clear()
                    else:
                        del new_coef_dict[r]['weak_mod']
                if duty == 'duty8':
                    new_coef_dict[r].update({'duty': duty})
                r_coefs = {k: named_coefs[k] for k in named_coefs if k in self.named_coefficients[r] if named_coefs[k]}
                new_coef_dict[r].update(r_coefs)
                new_coef_dict[r] = [i for i in list(new_coef_dict[r].values()) if i]

            #print(new_coef_dict)
            return new_coef_dict
        self.mods_frame['named_coefs'] = list(map(named_coefs,
                                                  self.mods_frame['positions'],
                                                  self.mods_frame['duty'],
                                                  self.mods_frame['with_children'],
                                                  mods_for_coef.values(),
                                                  named_mods.values()))


class CategoryData:
    def __init__(self, active_recipient, cf, mf, pf, date_frame=''):
        self.active_recipient = active_recipient
        self.name = cf.name
        self.cat_frame = pd.DataFrame([True if i == 'T' else i for i in cf], columns=[self.name])
        self.true_count = 0
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
                if price >= 0:
                    self.true_count += 1
            else:
                price = price_calc[result]
                self.true_count += 1
        else:
            price = price_calc[result]
        #print(price)

        return {'price': price, 'price_calc': price_calc}

    def add_price_column(self, show_calculation=False):
        self.cat_frame['positions'] = self.mod_frame['positions'].map(lambda e: e[self.active_recipient])
        price_list = list(map(self.find_a_price,
                              self.mod_frame['duty'],
                              self.cat_frame[self.name],
                              self.cat_frame['positions']))
        self.cat_frame['price'] = [i.pop('price') for i in price_list]
        if show_calculation:
            price_list = [list(i.values())[0] for i in price_list]
            self.cat_frame.insert(self.cat_frame.columns.get_loc('price'), 'price_calc', price_list)
            #print(self.cat_frame)
            #print(self.mod_frame[['zlata_mod', 'duty_mod', 'positions']])
        return self.cat_frame

    def count_a_modification(self, coefs):
        recipient_coefs = coefs[self.active_recipient]
        coefficient_dict = {}
        for coef in recipient_coefs:
            if type(coef) == dict:
                coef = recipient_coefs.pop(recipient_coefs.index(coef))
                key, value = list(coef)[0], coef[list(coef)[0]]
                coef = eval(self.price_frame[key])[value] if type(self.price_frame[key]) == str else self.price_frame[key]
                coefficient_dict[key] = coef
        coefficient_dict.update({i: self.price_frame[i] if i in self.price_frame else 1 for i in recipient_coefs})
        coefficient_dict['coef'] = np.array(list(coefficient_dict.values())).prod()
        #print(coefficient_dict)
        return coefficient_dict

    def total_count(self, price, coef):
        if price > 0:
            price *= coef
        return round(price, 2)

    def add_coef_and_result_column(self, show_calculation=False):
        coefs_list = list(map(self.count_a_modification, self.mod_frame['named_coefs']))
        self.cat_frame['coef'] = [i.pop('coef') for i in coefs_list]
        self.cat_frame['result'] = list(map(self.total_count, self.cat_frame['price'], self.cat_frame['coef']))
        if show_calculation:
            self.cat_frame.insert(self.cat_frame.columns.get_loc('coef'), 'with_children', self.mod_frame['with_children'])
            self.cat_frame.insert(self.cat_frame.columns.get_loc('coef'), 'coef_count', coefs_list)
            #print(self.cat_frame)
        return self.price_frame
