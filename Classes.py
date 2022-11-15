import csv
from programm import table_reader


def price_reader():
    with open('months/sept22/price.csv', 'r') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            print(row)


price_reader()











class ObjectPrice:

    def __init__(self, name, price):
        self.name = name
        self.price = price

    def sum_of_price(self, num):
        return num + self.price


x, y = ObjectPrice('jopa', 50), ObjectPrice('gabber', 100)
print(x.sum_of_price(50), y.sum_of_price(50))

