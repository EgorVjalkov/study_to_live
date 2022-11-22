import csv


modificators = ['MOD', 'WEAK', 'DUTY']
date = ['DATE', 'DAY']
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
        if cell_price > 0:

            modification = 1
            if self.duty_day:
                modification *= float(self.price['duty_8'].replace(',', '.'))
                print(modification)
            if self.zlata_mod:
                modification *= float(self.price[self.zlata_mod].replace(',', '.'))
                print(modification)
            if self.weak_child:
                weak_key = 'WEAK' + self.weak_child
                modification *= float(self.price[weak_key].replace(',', '.'))
            print(modification)

        return modification

    #запили мадификацию кудато
    def find_a_recipients(self, cell_price):

        recipients = {'Egr': 0, 'Lera': 0}
        if self.on_duty and not self.duty_day:
            positions = {'Lera': ['A', 'L', 'Z', 'F'], 'Egr': ['E']}
        else:
            positions = {'Lera': ['A', 'L'], 'Egr': ['E'], 'All': ['Z', 'F']}
        for k in positions:
            if self.identificator in positions[k]:
                if k == 'All':
                    recipients = {k: cell_price for k in recipients}
                else:
                    recipients[k] = cell_price
        return recipients
# остановилисть на внедрении в расчет дежурств


with open('months/oct22/vedomost.csv', 'r') as f:
    calendary = csv.DictReader(f, delimiter=';')
    for row in calendary:
        mods = {k: row[k] for k in row if k in modificators}
        category = {k: row[k] for k in row if k not in modificators}
        category = {k: category[k] for k in category if k not in date}
        print(mods)
        print('\n')
        for i in category:
            i = CategoryInDay(i, category[i], prices, mods)
            print(i.zlata_mod, i.on_duty, i.duty_day, i.weak_child)
            print(i.name, i.result, i.find_a_recipients(i.find_a_price()))
            print('\n')

#           нада подумать кателок поварить как лаконичнее через классы вывести цену дня
# сделай мини программу класс которая работает с подобного типа данными. Слей 2 словаря в один
# там и будет логика и поведение
        # if row['duty']:
        #     if row['duty'] == '24':
        #         Lera_category.extend(Family_category)


