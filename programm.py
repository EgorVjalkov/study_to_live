import csv


modificators = ['MOD', 'WEAK', 'DUTY']
date_keys = ['DATE', 'DAY']

EGR = 0
LERA = 0
EGR_meals = 0
LERA_meals = 0

MONTH = 'months/nov22/'


def long_box_read():
    recipients = {'Egr': 0, 'Lera': 0}
    with open(f'{MONTH}longbox.csv', 'r') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            name = row['name']
            if name and name != '0':
                if row['mod'] == 'long_box':
                    if input(f'"{name}" is done? ') == 'y':
                        if name[0] == 'E':
                            recipients['Egr'] += int(row['price'])
                        elif name[0] == 'L':
                            recipients['Lera'] += int(row['price'])
                        else:
                            recipients['Egr'] += int(row['price']) / 2
                            recipients['Lera'] += int(row['price']) / 2
                    print(recipients)

                if row['mod'] == 'fine/enc':
                    egr_count = input(f'How match "{name}" Egr does? ')
                    if egr_count:
                        recipients['Egr'] += int(egr_count) * int(row['price'])
                    lera_count = input(f'How match "{name}" Lera does? ')
                    if lera_count:
                        recipients['Lera'] += int(lera_count) * int(row['price'])
                    print(recipients)
        return recipients


def complex_condition(result, condition_for_price):
    if ':' in condition_for_price:
        condition_for_price = dict([i.split(': ') for i in condition_for_price .split(', ')])
        # print(condition_for_price[result])
        price_of_day = int(condition_for_price[result])
    elif '*' in condition_for_price:
        price_of_day = int(condition_for_price.replace('*', '')) * int(result)
    return price_of_day

# print(int_or_complex_condition('', '50'))


with open(f'{MONTH}price.csv', 'r') as f:
    read = csv.DictReader(f, delimiter=';')
    prices = {}
    for day in read:
        name = day['category']
        del day['category']
        prices[name] = day
    # print(prices)


class CategoryInDay:
    def __init__(self, name_of_category, result_of_day, prices, mods):
        self.name = name_of_category
        self.meals = True if 'MEALS'in self.name else False
        self.first_char = self.name[0]
        self.result = result_of_day
        if self.result == 'T':
            self.result = True
        if not self.result:
            self.result = False
        self.price = prices[self.name]
# сделана 1/2 на All разбоки с нулем
        self.on_duty = True if mods['DUTY'] and mods['DUTY'] != '0' else False
        self.duty24 = True if mods['DUTY'] == '24' else False
        self.duty_day = True if mods['DUTY'] == '8' else False
        self.weak_child_mod = mods['WEAK']
        self.zlata_mod = mods['MOD']
        self.mother_mod = True if self.zlata_mod == 'M' else False
        self.coefficient = self.modification()

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
            cell_price = int(cell_price[self.result])
        else:
            cell_price = complex_condition(self.result, cell_price[True])

        return cell_price

    def modification(self):
        modification = 1
        if self.duty_day:
            modification *= float(self.price['duty_8'].replace(',', '.'))
            # print('8', modification)
        if self.zlata_mod:
            modification *= float(self.price[self.zlata_mod].replace(',', '.'))
            # print('Z', modification)
        if self.weak_child_mod:
            weak_key = 'WEAK' + self.weak_child_mod
            modification *= float(self.price[weak_key].replace(',', '.'))
            # print('W', modification)
        return modification

    def find_a_recipients(self, cell_price):
        container = {'Egr': 0, 'Lera': 0}
        if self.recipient == 'All':
            container = {k: cell_price for k in container}
        else:
            container[self.recipient] = cell_price
        print('premod', container)

        if cell_price <= 0:
            self.coefficient = 0
        else:
            if self.only_lera_mod:
                if 'Lera' in container:
                    container['Lera'] *= self.coefficient
            else:
                container = {k: container[k] * self.coefficient for k in container}

        return container


with open(f'{MONTH}vedomost.csv', 'r') as f:
    calendary = csv.DictReader(f, delimiter=';')
    for day in calendary:
        mods = {k: day[k] for k in day if k in modificators}
        category = {k: day[k] for k in day if k not in modificators}
        date = {k: day[k] for k in day if k in date_keys}
        category = {k: category[k] for k in category if k not in date_keys}
        print(date, mods)
        print('')
        for i in category:
            i = CategoryInDay(i, category[i], prices, mods)
            print(i.name, i.result)
            print('Z', i.zlata_mod, ', D', i.on_duty, ', 8', i.duty_day, ', W', i.weak_child_mod, i.coefficient)
            pay_a_day = i.find_a_recipients(i.find_a_price())
            print('postmod', pay_a_day)

            if i.meals:
                EGR_meals += pay_a_day['Egr']
                LERA_meals += pay_a_day['Lera']
            else:
                EGR += pay_a_day['Egr']
                LERA += pay_a_day['Lera']
            print(EGR, EGR_meals, LERA, LERA_meals)
            print('')

    counted = {'Egr': EGR, 'Egr_meals': EGR_meals, 'Lera': LERA, 'Lera_meals': LERA_meals}
    counted = {k: round(counted[k], 2) for k in counted}
    print(counted)
    long_box_dict = long_box_read()
    for k in counted:
        if k in long_box_dict:
            counted[k] += long_box_dict[k]
    print(counted)
