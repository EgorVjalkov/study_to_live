import pandas as pd
from random import choice, randint
import datetime
import numpy as np

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
        self.result = result
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
                self.result = datetime.datetime.combine(self.date, time)
                if self.result.hour < 8:
                    self.result += datetime.timedelta(days=1)

            # elif self.result.isdigit():
            #     print(self.result)
            #     self.result = int(self.result)

        self.type_result = type(self.result)
        # print(self.type_result)

        return self.result, self.type_result

    def prepare_condition_for_price(self):
        if ':' in self.condition_for_price:
            self.condition_for_price = dict([i.split(': ') for i in self.condition_for_price.split(', ')])
        return self.condition_for_price

    def get_price_if_datetime(self):
        delta = 0
        for k in self.condition_for_price:
            if '.' in k:
                inner_condition = k.split('.')
                if inner_condition[0] in self.comparison_dict:
                    comparison_operator = inner_condition[0]
                    comparison_value = datetime.time(int(inner_condition[1]))
                    comparison_value = datetime.datetime.combine(self.date, comparison_value)
                    if comparison_value.hour < 8:
                        comparison_value += datetime.timedelta(days=1)
                    # print(self.result, comparison_value)

                    inner_condition = self.comparison_dict[comparison_operator](self.result, comparison_value)
                    if inner_condition:
                        if '*' in self.condition_for_price[k]:
                            if not delta:
                                if comparison_value > self.result:
                                    delta = (comparison_value - self.result).seconds / 60
                                else:
                                    delta = (self.result - comparison_value).seconds / 60
                            else:
                                delta = 60
                            divider = float(self.condition_for_price[k].replace('*', ''))
                            self.price += delta * divider
                            # print(delta)
                        else:
                            self.price += int(self.condition_for_price[k])
                        # print(k, self.condition_for_price[k], inner_condition, self.price)

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

# cc = ComplexCondition('20,31', '<.22: 3*, <.23: 2*, >=.23: 0')
# #cc = ComplexCondition(4, '40*')
# cc.prepare_result()
# cc.prepare_condition_for_price()
# print(cc.get_price())


class MonthData:

        self.egr_count = 0
        self.lera_count = 0
        self.egr_meals = 0
        self.lera_meals = 0

    def collect_all_in_month(self, day_container):
        self.egr_count += day_container['money']['Egr']
        self.egr_meals += day_container['meals']['Egr']
        self.lera_count += day_container['money']['Lera']
        self.lera_meals += day_container['meals']['Lera']
        return self.egr_count, self.egr_meals, self.lera_count, self.lera_meals


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

        self.workday_result = {}
        self.meals_result = {}
        self.container = {}

    def collect_all(self, bag, container):
        del bag['code']
        if not container:
            container = bag.copy()
        else:
            container = {k: container[k] + bag[k] for k in container}
        container = {k: round(container[k]) for k in container}
        return container

    def sort_to_containers(self, bag):
        if 'meals' in bag.values():
            self.meals_result = self.collect_all(bag, self.meals_result)
            self.container['meals'] = self.meals_result
        else:
            self.workday_result = self.collect_all(bag, self.workday_result)
            self.container['money'] = self.workday_result
        return self.container




class CategoryPrice:
    def __init__(self, name, result, mods, duty, prices):
        self.name = name
        self.meals = True if 'MEALS' in self.name else False
        self.first_char = self.name[0]

        self.result = result

        self.zlata_mod = mods['MOD']
        self.weak_child_mod = mods['WEAK']

        self.volkhov_alone_mod = True if self.zlata_mod == 'M' else False
        self.on_duty = True if duty or self.volkhov_alone_mod else False
        self.duty24 = True if duty == 24 or self.volkhov_alone_mod else False
        self.duty_day = True if duty == 8 else False

        self.price = [i for i in prices if self.name in i.values()][0]
        self.category_price = 0
        self.coefficient_dict = {}
        self.coefficient = 0

        self.money_bag = {}

        if self.duty24:
            self.positions = {'Lera': ['A', 'L', 'Z', 'F'], 'Egr': ['E']}
            self.only_lera_mod = True
        else:
            self.positions = {'Lera': ['L'], 'Egr': ['E'], 'All': ['A', 'Z', 'F']}
            self.only_lera_mod = False
        for k in self.positions:
            if self.first_char in self.positions[k]:
                self.recipient = k

    def find_a_price(self):
        cell_price = {True: self.price['True'], False: self.price['False']}
        if self.on_duty:
            cell_price[False] = self.price['duty_False']
            cell_price[True] = self.price['duty_24']
        print(self.name, self.result, cell_price)

        if type(self.result) == bool:
            self.category_price = int(cell_price[self.result])
        else:
            self.category_price = ComplexCondition(self.result, cell_price[True]).get_price()
        print('price', self.category_price)

        return self.category_price

    def count_a_modification(self):
        if self.duty_day:
            mod = float(self.price['duty_8'].replace(',', '.'))
            self.coefficient_dict['duty_8'] = mod
        if self.zlata_mod:
            mod = float(self.price[self.zlata_mod].replace(',', '.'))
            self.coefficient_dict['zlata_mod'] = mod
        if self.weak_child_mod:
            weak_key = 'WEAK' + str(self.weak_child_mod)
            mod = float(self.price[weak_key].replace(',', '.'))
            self.coefficient_dict[weak_key] = mod
        self.coefficient = np.array(list(self.coefficient_dict.values())).prod()
        print('coef', self.coefficient_dict, self.coefficient)
        return self.coefficient_dict, self.coefficient

    def total_count_and_save_in_dict(self):
        self.find_a_price()

        bag = {'Egr': 0, 'Lera': 0}
        if self.recipient == 'All':
            bag = {k: self.category_price for k in bag}
        else:
            bag[self.recipient] = self.category_price

        if self.category_price > 0:
            self.count_a_modification()

            if self.only_lera_mod:
                bag['Lera'] *= self.coefficient
            else:
                bag = {k: bag[k] * self.coefficient for k in bag}

        self.money_bag = bag.copy()

        if self.meals:
            self.money_bag['code'] = 'meals'
        else:
            self.money_bag['code'] = 'money'

        return self.money_bag


month_data = MonthData('tests/new_test.csv', 'months/dec22test/price.csv', ',')


for day in month_data.vedomost:
    day_data = Day(day)
    for i in day_data.categories:
        print('!!!!!!!', 'duty', day_data.duty, day_data.mods)
        category = CategoryPrice(i, day_data.categories[i], day_data.mods, day_data.duty, month_data.prices)
        bag = category.total_count_and_save_in_dict()
        containers = day_data.sort_to_containers(bag)
        # print(category.positions)
        print(bag)
        print(containers, '\n')
    month_data.collect_all_in_month(containers)

print(month_data.egr_count, month_data.egr_meals, month_data.lera_count, month_data.lera_meals)




