import csv


modificators = ['DATE', 'DAY', 'MOD', 'WEAK', 'DUTY']
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

def complex_condition(result, condition_for_price):
    if ':' in condition_for_price:
        condition_for_price = dict([i.split(': ') for i in condition_for_price .split(', ')])
        # print(condition_for_price[result])
        price_of_day = int(condition_for_price[result])
    elif '*' in condition_for_price:
        price_of_day = int(condition_for_price.replace('*', '')) * int(result)
    return price_of_day

# print(int_or_complex_condition('', '50'))


with open('months/oct22/price.csv', 'r') as f:
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
        self.identificator = self.name[0]
        self.result = result_of_day
        if self.result == 'T':
            self.result = True
        if not self.result:
            self.result = False
        self.price = prices[self.name]

    {'date': '01.09.2022', 'DAY': '4', 'mod': 'KG', 'weak': '', 'duty': '24'}

    def find_a_price(self, mods):
        cell_price = {True: self.price['True'], False: self.price['False']}
        if mods['DUTY']:
            cell_price[False] = self.price['duty_False']
            if mods['DUTY'] == '24':
                cell_price[True] = self.price['duty_24']
        # print('\n', cell_price)

        if type(self.result) == bool:
            cell_price = int(cell_price[self.result])
        else:
            cell_price = complex_condition(self.result, cell_price[True])
        return cell_price

    def who_gets_how_match(self, found_price):
        recipients = {'Egr': 0, 'Lera': 0}
        positions = {'Lera': ['A', 'L'], 'Egr': ['E'], 'All': ['Z', 'F']}
        for k in positions:
            if self.identificator in positions[k]:
                if k == 'All':
                    recipients = {k: found_price for k in recipients}
                else:
                    recipients[k] = found_price
        return recipients
# остановилисть на внедрении в расчет дежурств


with open('months/oct22/vedomost.csv', 'r') as f:
    calendary = csv.DictReader(f, delimiter=';')
    for row in calendary:
        mods = {k: row[k] for k in row if k in modificators}
        category = {k: row[k] for k in row if k not in modificators}
        print(category)
        for i in category:
            i = CategoryInDay(i, category[i], prices)
            print(i.name, i.result, i.find_a_price(mods))
            print(i.who_gets_how_match(i.find_a_price(mods)))

        break
#           нада подумать кателок поварить как лаконичнее через классы вывести цену дня
# сделай мини программу класс которая работает с подобного типа данными. Слей 2 словаря в один
# там и будет логика и поведение
        # if row['duty']:
        #     if row['duty'] == '24':
        #         Lera_category.extend(Family_category)


