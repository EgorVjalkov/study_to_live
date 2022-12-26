import csv
from Classes import Vedomost

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


with open(f'{MONTH}price.csv', 'r') as f:
    read = csv.DictReader(f, delimiter=';')
    prices = {}
    for day in read:
        name = day['category']
        del day['category']
        prices[name] = day
    # print(prices)


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
            i = Vedomost(i, category[i], prices, mods)
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

