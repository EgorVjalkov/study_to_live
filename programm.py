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


def price_reader():
    with open('months/sept22/price.csv', 'r') as f:
        read = csv.DictReader(f, delimiter=';')

# reformat in dict
with open('months/sept22/vedomost.csv', 'r') as f:
    calendary = csv.DictReader(f, delimiter=';')
    for row in calendary:
        mods = {k: row[k] for k in row if k in modificators}
        category = {k: row[k] for k in row if k not in modificators}

#           нада подумать кателок поварить как лаконичнее через классы вывести цену дня
# сделай мини программу класс которая работает с подобного типа данными. Слей 2 словаря в один
# там и будет логика и поведение
        # if row['duty']:
        #     if row['duty'] == '24':
        #         Lera_category.extend(Family_category)


