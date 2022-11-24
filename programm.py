import csv


modificators = ['MOD', 'WEAK', 'DUTY']
date_keys = ['DATE', 'DAY']

EGR = 0
LERA = 0
EGR_meals = 0
LERA_meals = 0

MONTH = 'months/oct22/'

def long_box_read():
    recipients = {'EGR': 0, 'LERA': 0}
    with open(f'{MONTH}longbox.csv', 'r') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            name = row['name']
            if row['mod'] == 'long_box':
                if input(f'"{name}" is done? ') == 'y':
                    if name[0] == 'E':
                        recipients['EGR'] += int(row['price'])
                    if name[0] == 'L':
                        recipients['LERA'] += int(row['price'])
                print(recipients)
            if row['mod'] == 'fine/enc':
                egr_count = int(input(f'How match "{name}" Egr does? '))
                recipients['EGR'] += (egr_count * int(row['price']))
                lera_count = int(input(f'How match "{name}" Lera does? '))
                recipients['LERA'] += (lera_count * int(row['price']))
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
        self.identificator = self.name[0]
        self.result = result_of_day
        if self.result == 'T':
            self.result = True
        if not self.result:
            self.result = False
        self.price = prices[self.name]
        self.on_duty = True if mods['DUTY'] else False
        self.duty_day = True if mods['DUTY'] == '8' else False
        self.weak_child = mods['WEAK']
        self.zlata_mod = mods['MOD']

    def find_a_price(self):
        cell_price = {True: self.price['True'], False: self.price['False']}
        if self.on_duty:
            cell_price[False] = self.price['duty_False']
            cell_price[True] = self.price['duty_24']
        print(cell_price)

        if type(self.result) == bool:
            cell_price = int(cell_price[self.result])
        else:
            cell_price = complex_condition(self.result, cell_price[True])


        return cell_price

    def modification(self, cell_price):
        modification = 1
        if cell_price > 0:
            if self.duty_day:
                modification *= float(self.price['duty_8'].replace(',', '.'))
                print('8', modification)
            if self.zlata_mod:
                modification *= float(self.price[self.zlata_mod].replace(',', '.'))
                print('Z', modification)
            if self.weak_child:
                weak_key = 'WEAK' + self.weak_child
                modification *= float(self.price[weak_key].replace(',', '.'))
                print('W', modification)
        return modification

    def find_a_recipients(self, cell_price):
        recipients = {'Egr': 0, 'Lera': 0}
        meals = {'Egr': 0, 'Lera': 0}
        if self.on_duty and not self.duty_day:
            positions = {'Lera': ['A', 'L', 'Z', 'F'], 'Egr': ['E']}
        else:
            positions = {'Lera': ['A', 'L'], 'Egr': ['E'], 'All': ['Z', 'F']}
        for k in positions:
            if self.identificator in positions[k]:
                if k == 'All':
                    recipients = {k: cell_price for k in recipients}
                else:
                    if 'MEALS' in self.name:
                        meals[k] = cell_price
                    else:
                        recipients[k] = cell_price
        print(recipients, meals)
        if self.on_duty and not self.duty_day:
            recipients['Lera'] *= self.modification(cell_price)
            meals['Lera'] *= self.modification(cell_price) if self.meals else cell_price!!!!!!!!!!!!!!!!!!!! додумай
        else:
            if 'MEALS' in self.name:
                meals = {k: meals[k] * self.modification(cell_price) for k in meals}
            else:
            recipients = {k: recipients[k] * self.modification(cell_price) for k in recipients}
            print(meals)
        result = dict([('recipients', recipients), ('meals', meals)])
        return result


with open(f'{MONTH}vedomost.csv', 'r') as f:
    calendary = csv.DictReader(f, delimiter=';')
    for day in calendary:
        mods = {k: day[k] for k in day if k in modificators}
        category = {k: day[k] for k in day if k not in modificators}
        date = {k: day[k] for k in day if k in date_keys}
        category = {k: category[k] for k in category if k not in date_keys}
        print(mods, date)
        print('\n')
        for i in category:
            i = CategoryInDay(i, category[i], prices, mods)
            print('Z', i.zlata_mod, 'D', i.on_duty, '8', i.duty_day, 'W', i.weak_child)
            pay_a_day = i.find_a_recipients(i.find_a_price())
            meals_a_day = pay_a_day.pop('meals')
            pay_a_day = pay_a_day.pop('recipients')
            print(i.name, i.result, pay_a_day)
            EGR += pay_a_day['Egr']
            EGR_meals += meals_a_day['Egr']
            LERA += pay_a_day['Lera']
            LERA_meals += meals_a_day['Lera']

            print(EGR, EGR_meals, LERA, LERA_meals)
            print('\n')

# long_box_read()
