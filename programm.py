import csv

Lera_category = ['A', 'L']
Egr_category = ['E']
Family_category = ['Z', 'F']

modificators = ['date', 'DAY', 'mod', 'weak', 'duty']
# def duty_check(row):


def long_box_read():
    lera = 0
    egr = 0
    with open('months/sept22/longbox.csv', 'r') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            name = row['name']
            if row['mod'] == 'long_box':
                if input(f'"{name}" is done? ') == 'y':
                    if name[0] == 'E':
                        egr += int(row['price'])
                        print(f'Egr has {egr}')
                    if name[0] == 'L':
                        lera += int(row['price'])
                        print(f'Lera has {lera}')
            if row['mod'] == 'fine/enc':
                egr_count = int(input(f'How match "{name}" Egr does? '))
                egr += (egr_count * int(row['price']))
                print(egr)
                lera_count = int(input(f'How match "{name}" Lera does? '))
                lera += (lera_count * int(row['price']))
                print(lera)
        print(egr, lera)


# long_box_read()


with open('months/sept22/price.csv', 'r') as f:
    read = csv.DictReader(f, delimiter=';')
    prices = {}
    for row in read:
        name = row['category']
        del row['category']
        prices[name] = row
    # print(prices)

class CategoryInDay:
    def __init__(self, name_of_category, result_of_day, prices):
        self.name = name_of_category
        self.result = result_of_day
        self.price = prices[self.name]

    {'date': '01.09.2022', 'DAY': '4', 'mod': 'KG', 'weak': '', 'duty': '24'}
    {'A: gym': {'duty_24': '50', 'duty_8': '37,5', 'duty_False': '0', 'True': '25', 'False': '0', 'func': '', 'WEAK1': '1.25', 'WEAK2': '1.5', 'KG': '0.5', 'KGD': '0.75', 'M': '1'},
     'A: bad': {'duty_24': '50', 'duty_8': '37,5', 'duty_False': '0', 'True': '25', 'False': '0', 'func': '', 'WEAK1': '1.25', 'WEAK2': '1.5', 'KG': '0.5', 'KGD': '0.75', 'M': '1'},
     'F: stroll mod': {'duty_24': '1, 50; 2, 100', 'duty_8': '1, 37; 2, 75', 'duty_False': '0', 'True': '50', 'False': '-50', 'func': 'comp', 'WEAK1': '1.25', 'WEAK2': '1.5', 'KG': '0.5', 'KGD': '0.75', 'M': '1'},
     'Z: velo': {'duty_24': '50', 'duty_8': '37,5', 'duty_False': '0', 'True': '50', 'False': '0', 'func': '', 'WEAK1': '1.25', 'WEAK2': '1.5', 'KG': '0.5', 'KGD': '0.75', 'M': '1'},
     'Z: sleep': {'duty_24': '>0, 50; >1, 100', 'duty_8': '>0, 37; >1, 75', 'duty_False': '0', 'True': '>1, 50', 'False': '-50', 'func': 'comp', 'WEAK1': '1.25', 'WEAK2': '1.5', 'KG': '0.5', 'KGD': '0.75', 'M': '1'},
     'Z: teeth': {'duty_24': '50', 'duty_8': '50', 'duty_False': '0', 'True': '50', 'False': '-50', 'func': '', 'WEAK1': '1.25', 'WEAK2': '1.5', 'KG': '0.5', 'KGD': '0.75', 'M': '1'}, 'Z: tele': {'duty_24': '300', 'duty_8': '225', 'duty_False': '0', 'True': '50', 'False': '-50', 'func': '', 'WEAK1': '1.25', 'WEAK2': '1.5', 'KG': '0.5', 'KGD': '0.75', 'M': '0,5'}, 'F: wash': {'duty_24': '50', 'duty_8': '37,5', 'duty_False': '0', 'True': '0', 'False': '-50', 'func': '', 'WEAK1': '1.25', 'WEAK2': '1.5', 'KG': '0.5', 'KGD': '0.75', 'M': '1'}, 'F: no pleasure': {'duty_24': '100', 'duty_8': '100', 'duty_False': '0', 'True': '100', 'False': '0', 'func': '', 'WEAK1': '1.25', 'WEAK2': '1.5', 'KG': '0.5', 'KGD': '0.75', 'M': '1'}, 'E: hygine': {'duty_24': '0', 'duty_8': '0', 'duty_False': '-50', 'True': '50', 'False': '0', 'func': '', 'WEAK1': '1.25', 'WEAK2': '1.5', 'KG': '0.5', 'KGD': '0.75', 'M': '0'}, 'E: py': {'duty_24': '50', 'duty_8': '50', 'duty_False': '-50', 'True': '50', 'False': '0', 'func': '', 'WEAK1': '1.25', 'WEAK2': '1.5', 'KG': '0.5', 'KGD': '0.75', 'M': '0'}, 'E: vim': {'duty_24': '50', 'duty_8': '50', 'duty_False': '-50', 'True': '50', 'False': '0', 'func': '', 'WEAK1': '1.25', 'WEAK2': '1.5', 'KG': '0.5', 'KGD': '0.75', 'M': '0'}, 'E: plan': {'duty_24': '100', 'duty_8': '100', 'duty_False': '0', 'True': '100', 'False': '0', 'func': '', 'WEAK1': '1.25', 'WEAK2': '1.5', 'KG': '0.5', 'KGD': '0.75', 'M': '0'}, 'E: diet': {'duty_24': '0', 'duty_8': '0', 'duty_False': '-50', 'True': '50', 'False': '0', 'func': '', 'WEAK1': '1.25', 'WEAK2': '1.5', 'KG': '0.5', 'KGD': '0.75', 'M': '0'}, 'E: meals': {'duty_24': '10*num', 'duty_8': '10*num', 'duty_False': '0', 'True': '10*num', 'False': '0', 'func': 'num', 'WEAK1': '1.25', 'WEAK2': '1.5', 'KG': '1', 'KGD': '1', 'M': '1'}, 'L: teeth': {'duty_24': '50', 'duty_8': '50', 'duty_False': '0', 'True': '50', 'False': '-50', 'func': '', 'WEAK1': '1.25', 'WEAK2': '1.5', 'KG': '0.5', 'KGD': '0.75', 'M': '1'}, 'L: diet': {'duty_24': '50', 'duty_8': '50', 'duty_False': '0', 'True': '50', 'False': '-50', 'func': '', 'WEAK1': '1.25', 'WEAK2': '1.5', 'KG': '0.5', 'KGD': '0.75', 'M': '1'}, 'L: meals': {'duty_24': '30*num', 'duty_8': '30*num', 'duty_False': '0', 'True': '20*num', 'False': '0', 'func': 'num', 'WEAK1': '1.25', 'WEAK2': '1.5', 'KG': '1', 'KGD': '1', 'M': '1.5'}}

    def find_a_price(self, mods, price):
        cell_price = {True: prices['True'], False: prices['False']}
        if mods['duty'] == 24:
            cell_price[True] = prices['duty_24']


        if mods['mod'] == 8:
            pass
        mods = {k: mods[k] for k in mods if mods[k]}


       # карочи мы имеем категорию со значением в этой феккции попытаемся определить ее цену в зависимости от модика и цен


# reformat in dict
with open('months/sept22/vedomost.csv', 'r') as f:
    calendary = csv.DictReader(f, delimiter=';')
    for row in calendary:
        mods = {k: row[k] for k in row if k in modificators}
        category = {k: row[k] for k in row if k not in modificators}
        print(category)
        for i in category:
            i = CategoryInDay(i, category[i], prices)
            print(i.name, i.result, i.price)
            break
        break
#           нада подумать кателок поварить как лаконичнее через классы вывести цену дня
# сделай мини программу класс которая работает с подобного типа данными. Слей 2 словаря в один
# там и будет логика и поведение
        # if row['duty']:
        #     if row['duty'] == '24':
        #         Lera_category.extend(Family_category)


