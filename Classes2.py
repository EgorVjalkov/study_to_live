import pandas as pd
from ComplexCondition import ComplexCondition
import numpy as np

pd.set_option('display.max.columns', None)
class MonthData:
    def __init__(self, path, recipients):
        vedomost = pd.read_excel(path, sheet_name='vedomost').fillna(False)
        self.limit = len([i for i in vedomost['DATE'].to_list() if i])
        self.vedomost = vedomost[0:self.limit].fillna(0)
        self.prices = pd.read_excel(path, sheet_name='price', index_col=0).fillna(0)
        date_keys = ['DATE', 'DAY']
        self.accessory = self.vedomost.get([i for i in self.vedomost if i == i.upper() and i not in date_keys])
        self.date = self.vedomost.get(date_keys)
        self.categories = self.vedomost.get([i for i in self.vedomost if i == i.lower()])
        self.meals_columns = [i for i in self.categories.columns if 'meals' in i]
        self.NOT_meals_columns = [i for i in self.categories.columns if 'meals' not in i]
        #self.date.loc[self.limit] = ['total count', '']
        self.recipients = {k: self.date for k in recipients}

    def get_named_vedomost(self, name):
        for col in self.categories:
            if [i for i in self.categories[col] if type(i) == str and name[0] in i]:
                print(2)
                for i in self.categories[col]:
                    i = ComplexCondition(result=i).prepare_result()
                    # stopped!!!!! нужно подогнать кондишн, и сделать именовнные фреймы
                #print(named)
            else:
                self.recipients[name] = self.recipients[name].join(self.categories[col])
        #print(self.recipients)
        return self.recipients

    def add_cat_sum_frame(self, dict_of_result_frame):
        for name in dict_of_result_frame:
            dict_of_result_frame[name][self.limit] = dict_of_result_frame[name].sum()
            self.recipients[name] = self.recipients[name].join(dict_of_result_frame[name])
            #print(self.recipients)
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
        self.mods_frame['DIF_DUTY_mod'] = ['DIF_DUTY: ' + str(int(i)) if i else i for i in self.af['DIF_DUTY']]
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
            mods_key = ', '.join([i for i in mods if i])
            if mods_key not in self.positions_logic:
                mods_key = ''
            return self.positions_logic[mods_key]
        self.mods_frame['positions'] = list(map(f_for_positions,
                                                self.mods_frame['duty_mod'],
                                                self.mods_frame['zlata_mod']))

# проблема в том что нужно сделать все, а потом проийтмсь коротким циклом по реципиентам и у каждого модится свой фрейм
class CategoryData:
    def __init__(self, cf, mf, pf, date_frame=''):
        self.name = cf.name
        if cf.dtypes == 'float':
            cf.astype('int')
        if 'time' in self.name:
            self.cat_frame = pd.DataFrame([i.replace(',', ':') if i else i for i in cf], columns=[self.name])
        else:
            self.cat_frame = pd.DataFrame([True if i == 'T' else i for i in cf], columns=[self.name])
        self.position = self.name[0].upper()
        self.price_frame = pf[self.name]
        self.mod_frame = mf
        self.recipients_frame_dict = {'Egr': pd.DataFrame(), 'Lera': pd.DataFrame()} # здесь можно сразу определить позиции и не делать лишнюю работу
        self.recipients_key = \
            {k[0]: self.recipients_frame_dict[k] for k in self.recipients_frame_dict.keys()} # не помню нах это нужно было...
        #print(self.recipients_key)
        self.named_coefficients = {'Egr': 'DIF_DUTY'}

    def find_a_price(self, duty, result):
        price_calc = {True: self.price_frame['True'], False: self.price_frame['False']}
        if duty:
            price_calc['duty'] = duty
            price_calc[False] = self.price_frame['dutyFalse']
            price_calc[True] = self.price_frame['dutyTrue']

        if type(result) == bool:
            if type(price_calc[result]) != str:
                price = int(price_calc[result])
            else:
                price = ComplexCondition(price_calc[result]).get_price()
        else:
            price = ComplexCondition(price_calc[True], result).get_price()

        return {'price': price, 'price_calc': price_calc}

    def add_price_column(self, show_calculation=False):
        price_list = list(map(self.find_a_price, self.mod_frame['duty_mod'], self.cat_frame[self.name]))
        self.cat_frame['price'] = [i.pop('price') for i in price_list]
        if show_calculation:
            price_list = [list(i.values())[0] for i in price_list]
            self.cat_frame.insert(self.cat_frame.columns.get_loc('price'), 'price_calc', price_list)
            print(self.cat_frame)
        return self.cat_frame

    def count_a_modification(self, *args):
        mods = [i for i in args if i]
        dict_mods = {}
        for i in mods:
            if ':' in i:
                item = mods.pop(mods.index(i)).split(': ')
                key, value = item[0], item[1]
                if type(self.price_frame[key]) == str:
                    dict_mods[key] = float(ComplexCondition(self.price_frame[key]).prepare_condition()[value])
                    dict_mods = {k: dict_mods[self.named_coefficients[k]] for k in self.named_coefficients}
# подумай как сделать тут, чтобы остались именованные коэффициенты
        coefficient_dict = {k: self.price_frame[k] for k in mods if k in self.price_frame}
        coefficient_dict['coef'] = np.array(list(coefficient_dict.values())).prod()
        coefficient_dict.update(dict_mods)
        return coefficient_dict

    def add_coef_column(self, show_calculation=False):
        mods = [self.mod_frame.to_dict('list')[i] for i in self.mod_frame.to_dict('list') if 'mod' in i]
        coefs_list = list(map(self.count_a_modification, *mods))
        self.cat_frame['coef'] = [i.pop('coef') for i in coefs_list]
        for name in self.named_coefficients.keys():
            self.cat_frame[name + '_coef'] = [i[name] if name in i else 1.0 for i in coefs_list]
        if show_calculation:
            self.cat_frame.insert(self.cat_frame.columns.get_loc('coef'), 'coef_count', coefs_list)
            print(self.cat_frame)
        #self.cat_frame['result'] = self.cat_frame['price'] * self.cat_frame['coef']
        return self.price_frame

    def total_count(self, recipient, price, recipient_who_coef, coef, named_coef, positions):
        # есть мысль, что здесь можно сильно упростить все
        if self.position not in positions:
            return 0
        elif self.position in positions and price <= 0:
            return price
        else:
            if recipient in recipient_who_coef:
                price *= coef * named_coef
            else:
                price *= named_coef
        return price

    def add_recipients_column(self, recipients=(), show_calculation=False):
        if not recipients:
            recipients = list(self.recipients_frame_dict.keys())
        for name in recipients:
            self.cat_frame[name+'_positions'] = self.mod_frame['positions'].map(lambda e: e[name])
            if name+'_coef' not in self.cat_frame.columns:
                self.cat_frame[name+'_coef'] = 1.00
            self.cat_frame[name] = list(map(self.total_count,
                                            pd.Series(name, index=self.cat_frame.index),
                                            self.cat_frame['price'],
                                            self.mod_frame['recipient_who_coef'],
                                            self.cat_frame['coef'],
                                            self.cat_frame[name+'_coef'],# !!!!!! СДЕЛАЙ РЕФАКТОР С ФУНКЦИЕЙ КОТОРАЯ СРАЗУ ОПРЕДЕЛЯЕТ ИМЕНОВАННЫЙ КОЭФФИЦИЕНТ
                                            self.cat_frame[name+'_positions']))
            if not show_calculation:
                del self.cat_frame[name+'_positions']
        if show_calculation:
            print(self.cat_frame)
        return self.cat_frame

    def get_a_result_column_in_dict(self):
        self.recipients_frame_dict = {rec_key: self.cat_frame[rec_key] for rec_key in self.recipients_frame_dict}
        self.recipients_frame_dict = \
            {rec_key: self.recipients_frame_dict[rec_key].rename(self.name) for rec_key in self.recipients_frame_dict}
        #print(self.recipients)
        return self.recipients_frame_dict


recipients = ['Egr', 'Lera']

jan23 = MonthData('months/jan23/jan23.xlsx', recipients)
for name in jan23.recipients:
    jan23.get_named_vedomost(name)
##print(jan23.categories)
##print(jan23.prices)
#ad = AccessoryData(jan23.accessory)
#ad.get_mods_frame()
#for cat in jan23.categories:
#    cat = 'z:stroll'
#    show_calc = False
#    cd = CategoryData(jan23.categories[cat], ad.mods_frame, jan23.prices)
#    print(cd.cat_frame)
#    cd.add_price_column(show_calc)
#    cd.add_coef_column(show_calc)
#    cd.add_recipients_column(show_calc)
#    cd.cat_frame = jan23.date.join(cd.cat_frame)
#    cd.cat_frame.set_index('DATE')
#    #cd.cat_frame.to_excel('months/jan23/jan23_results.xlsx', sheet_name=cat.replace(':', '_'))
#    jan23.add_cat_sum_frame(cd.get_a_result_column_in_dict())
#    #break
#for name in jan23.recipients: #сделай чтоб писало все
#    jan23.recipients[name].to_excel('months/jan23/jan23_results.xlsx', sheet_name=name+'_total')
#    total_count = jan23.recipients[name][jan23.NOT_meals_columns].tail(1).sum(1)
#    meals_count = jan23.recipients[name][jan23.meals_columns].tail(1).sum(1)
#    print(name, total_count, meals_count)
#print(jan23.recipients['Lera'])
