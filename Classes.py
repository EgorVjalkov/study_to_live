import pandas as pd
from random import choice, randint


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
            minutes += randint(1, 60)
            time.append(str(minutes))
            return ':'.join(time)

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

    def __init__(self, cell_value):
        self.value = cell_value

    def complex_condition(result, condition_for_price):
        if ':' in condition_for_price:
            condition_for_price = dict([i.split(': ') for i in condition_for_price .split(', ')])
            # print(condition_for_price[result])
            price_of_day = int(condition_for_price[result])
        elif '*' in condition_for_price:
            price_of_day = int(condition_for_price.replace('*', '')) * int(result)
        return price_of_day

# print(int_or_complex_condition('', '50'))

class MonthData:
    def __init__(self, path_to_vedomost, path_to_price):
        self.path_to_price = path_to_price
        self.vedomost = pd.read_csv(path_to_vedomost, delimiter=';')
        self.days = len(self.vedomost)
        self.prices = pd.read_csv(path_to_price, delimiter=';')


class Day:
    def __init__(self, data_frame, price_frame):
        day_df = data_frame.fillna(0).to_dict('list')
        day_df = {k: day_df[k][0] for k in day_df}
        day_df = {k: int(day_df[k]) if type(day_df[k]) == float else day_df[k] for k in day_df}
        self.data = {k: False if not day_df[k] else True if day_df[k] == 'T' else day_df[k] for k in day_df} # можн оперевести все в str

        self.prices = price_frame

        date_keys = ['DATE', 'DAY']
        self.date = {k: self.data.pop(k) for k in date_keys}
        mods_keys = ['MOD', 'WEAK']
        self.mods = {k: self.data.pop(k) for k in mods_keys}
        self.duty = self.data.pop('DUTY')
        self.categories = self.data

        self.coefficient = 1

    def count_a_coefficient(self):
        print(self.prices)
        # mod_frame = self.prices['MOD']


df = MonthData('months/nov22/vedomost.csv', 'months/nov22/price.csv')
# print(df.vedomost[0:df.limit])
for d in range(df.days):
    day_data = Day(df.vedomost[d:d+1], df.prices)
    print(day_data.date)
    print(day_data.categories)
    break

# for i in df.vedomost:

        # self.name = name_of_category
        # self.meals = True if 'MEALS'in self.name else False
        # self.first_char = self.name[0]
        # self.result = result_of_day
        # if self.result == 'T':
        #     self.result = True
        # if not self.result:
        #     self.result = False
        # self.price = prices[self.name]
        # сделана 1/2 на All разбоки с нулем
        # self.on_duty = True if mods['DUTY'] and mods['DUTY'] != '0' else False
        # self.duty24 = True if mods['DUTY'] == '24' else False
        # self.duty_day = True if mods['DUTY'] == '8' else False
        # self.weak_child_mod = mods['WEAK']
        # self.zlata_mod = mods['MOD']
        # self.mother_mod = True if self.zlata_mod == 'M' else False
        # self.coefficient = self.modification()
        #
        # if self.duty24:
        #     self.positions = {'Lera': ['A', 'L', 'Z', 'F'], 'Egr': ['E']}
        #     self.only_lera_mod = True
        # else:
        #     self.positions = {'Lera': ['A', 'L'], 'Egr': ['E'], 'All': ['Z', 'F']}
        #     self.only_lera_mod = True if self.mother_mod else False
        # for k in self.positions:
        #     if self.first_char in self.positions[k]:
        #         self.recipient = k
    #
    # def find_a_price(self):
    #     cell_price = {True: self.price['True'], False: self.price['False']}
    #     if self.on_duty:
    #         cell_price[False] = self.price['duty_False']
    #         cell_price[True] = self.price['duty_24']
    #     print('cellprice', cell_price)
    #
    #     if type(self.result) == bool:
    #         cell_price = int(cell_price[self.result])
    #     else:
    #         cell_price = complex_condition(self.result, cell_price[True])
    #
    #     return cell_price
    #
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
