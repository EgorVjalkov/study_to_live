import pandas as pd
from random import choice, randint
import datetime


class TestingPrices:
    def __init__(self, path_to_test, path_to_price=''):
        self.path_to_test = path_to_test
        self.path_to_price = path_to_price
        self.categories = {}
        self.test = []
        self.path_to_newtest = 'tests/new_test.csv'

    def read_and_filter(self):
        df = pd.read_csv(self.path_to_test, delimiter=';')
        limit = len([i for i in df['ANSWER'].fillna(0) if i > 0])
        df = df[0:limit]
        head = [i for i in df.columns.to_list() if 'Unnamed' not in i]
        variants = df[head]
        for key in variants:
            if key != 'ANSWER':
                variants[key] = [int(i) if type(i) == float else i for i in variants[key].fillna(0)]
                variants[key] = [str(i) if i else '' for i in variants[key]]
                self.categories[key] = variants[key].unique().tolist()
        return self.categories

    def create_a_testframe(self, days=1, category_key='', to_file=True):

        def testtime(time_list):
            time = choice(time_list).split(':')
            minutes = int(time.pop(1))
            minutes += randint(1, 59)
            time.append(str(minutes))
            return ','.join(time)

        # if category_key:
        #     testing_cats = input(f'Choose a category')

        self.test.clear()
        for i in range(days):
            day = {k: testtime((self.categories[k])) if 'TIME' in k else choice(self.categories[k]) for k in self.categories}
            self.test.append(day)

        if to_file:
            test_data_frame = pd.DataFrame(self.test)
            test_data_frame.to_csv(self.path_to_newtest, index=False)

        return self.test

class ComplexCondition:
    def __init__(self, result, condition_for_price, date=''):
        self.result = str(result)
        self.type_result = type(result)
        self.condition_for_price = condition_for_price
        self.date = datetime.date.today() if date == 'DATE' or not date else date
        self.comparison_dict = {'<': lambda r, y: r < y,
                                '<=': lambda r, y: r <= y,
                                '>=': lambda r, y: r >= y,
                                '>': lambda r, y: r > y}
        self.price = 0

    def prepare_result(self):
        if self.type_result == str:
            if ',' in self.result:
                time = [int(i) for i in self.result.split(',')]
                time = datetime.time(*time)
                if time.hour < 8:
                    self.result = datetime.datetime.combine(self.date + datetime.timedelta(days=1), time)
                self.result = datetime.datetime.combine(self.date, time)


            elif self.result.isdigit():
                self.result = int(self.result)

        self.type_result = type(self.result)

        return self.result, self.type_result

    def prepare_condition_for_price(self):
        if ':' in self.condition_for_price:
            self.condition_for_price = dict([i.split(': ') for i in self.condition_for_price.split(', ')])
        return self.condition_for_price

    def get_price_if_datetime(self):
        for k in self.condition_for_price:
            if '.' in k:
                inner_condition = k.split('.')
                if inner_condition[0] in self.comparison_dict:
                    comparison_operator = inner_condition[0]
                    comparison_value = datetime.time(int(inner_condition[1]))
                    comparison_value = datetime.datetime.combine(self.date, comparison_value)

                    inner_condition = self.comparison_dict[comparison_operator](self.result, comparison_value)

                    if inner_condition:
                        if comparison_value > self.result:
                            delta = (comparison_value - self.result).seconds / 60
                        else:
                            delta = (self.result - comparison_value).seconds / 60
# подумай с дельтой!!!
                        if '*' in self.condition_for_price[k]:
                            divider = float(self.condition_for_price[k].replace('*', ''))
                            self.price += delta * divider

        return int(self.price)

    def get_price(self):
        self.prepare_result()
        self.prepare_condition_for_price()
        if self.type_result == datetime.datetime:
            return self.get_price_if_datetime()
        if '*' in self.condition_for_price:
            divider = int(self.condition_for_price.replace('*', ''))
            self.price = divider * self.result
        else:
            self.price = int(self.condition_for_price)

        return self.price

cc = ComplexCondition('20,09', '<.22: 3*, <.23: 2*, >=.23: 0')
cc.prepare_result()
cc.prepare_condition_for_price()
print(cc.get_price_if_datetime())



class MonthData:
    def __init__(self, path_to_vedomost, path_to_price, delimiter):
        self.path_to_price = path_to_price
        self.vedomost = pd.read_csv(path_to_vedomost, delimiter=delimiter).fillna(0).to_dict('records') # read_exel, astype(type)
        self.days = len(self.vedomost)
        self.prices = pd.read_csv(path_to_price, delimiter=';').to_dict('records')


class Day:
    def __init__(self, dict_data):
        dict_data = {k: int(dict_data[k]) if type(dict_data[k]) == float else dict_data[k] for k in dict_data}
        self.data = {k: False if not dict_data[k] else True if dict_data[k] == 'T' else dict_data[k] for k in dict_data} # можн оперевести все в str

        date_keys = ['DATE', 'DAY']
        self.date = {k: self.data.pop(k) if k in self.data else k for k in date_keys}
        mods_keys = ['MOD', 'WEAK']
        self.mods = {k: self.data.pop(k) for k in mods_keys}
        self.duty = self.data.pop('DUTY')
        self.categories = self.data


class CategoryPrice:
    def __init__(self, name, result, mods, duty, prices):
        self.name = name
        self.meals = True if 'MEALS' in self.name else False
        self.first_char = self.name[0]
        self.result = result
        self.price = [i for i in prices if self.name in i.values()][0]
        self.on_duty = True if duty else False
        self.duty24 = True if duty == '24' else False
        self.duty_day = True if duty == '8' else False
        self.weak_child_mod = mods['WEAK']
        self.zlata_mod = mods['MOD']
        self.mother_mod = True if self.zlata_mod == 'M' else False

        self.cell_price = 0
        self.coefficient = 1

        if self.duty24:
            self.positions = {'Lera': ['A', 'L', 'Z', 'F'], 'Egr': ['E']}
            self.only_lera_mod = True
        else:
            self.positions = {'Lera': ['A', 'L'], 'Egr': ['E'], 'All': ['Z', 'F']}
            self.only_lera_mod = True if self.mother_mod else False
        for k in self.positions:
            if self.first_char in self.positions[k]:
                self.recipient = k

    def find_a_price(self):
        cell_price = {True: self.price['True'], False: self.price['False']}
        if self.on_duty:
            cell_price[False] = self.price['duty_False']
            cell_price[True] = self.price['duty_24']
        print('cellprice', cell_price)

        if type(self.result) == bool:
            self.cell_price = int(cell_price[self.result])
        else:
            self.cell_price = ComplexCondition(self.result, cell_price[True]).get_price()
            print(self.cell_price)

        return self.cell_price

    # def modification(self):
    #     modification = 1
    #     if self.duty_day:
    #         modification *= float(self.price['duty_8'].replace(',', '.'))
    #         print('8', modification)
    # if self.zlata_mod:
    #     modification *= float(self.price[self.zlata_mod].replace(',', '.'))
    #     print('Z', modification)
    # if self.weak_child_mod:
    #     weak_key = 'WEAK' + self.weak_child_mod
    #     modification *= float(self.price[weak_key].replace(',', '.'))
    #     print('W', modification)
    # return modification
    #
    # def find_a_recipients(self, cell_price):
    #     container = {'Egr': 0, 'Lera': 0}
    #     if self.recipient == 'All':
    #         container = {k: cell_price for k in container}
    #     else:
    #         container[self.recipient] = cell_price
    #     print('premod', container)
    #
    #     if cell_price <= 0:
    #         self.coefficient = 0
    #     else:
    #         if self.only_lera_mod:
    #             if 'Lera' in container:
    #                 container['Lera'] *= self.coefficient
    #         else:
    #             container = {k: container[k] * self.coefficient for k in container}
    #
    #     return container
    # def get_price(self):
    #
    # def get_coefficient(self):






    def get_a_price(self):
        print(self.prices)

    def count_a_coefficient(self):
        print(self.prices)
        # mod_frame = self.prices['MOD']


month_data = MonthData('tests/new_test.csv', 'months/dec22test/price.csv', ',')


for day in month_data.vedomost:
    day_data = Day(day)
    for i in day_data.categories:
        price = CategoryPrice(i, day_data.categories[i], day_data.mods, day_data.duty, month_data.prices)
        # print(i, day_data.date, price.result, price.find_a_price())



# for i in df.vedomost:

