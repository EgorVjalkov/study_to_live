import datetime
from random import choice

class ComplexCondition:
    def __init__(self, result='', condition='', date=''):
        #multiply_is = lambda i: i and '*' in i
        if '{' in condition:
            result = str(int(float(result))) if type(result) == float else str(result)
            condition = eval(condition)

        self.result = result
        self.condition_for_price = condition
        self.date = datetime.date.today() if date == 'DATE' or not date else date
        self.comparison_dict = {'<': lambda r, y: r < y,
                                '<=': lambda r, y: r <= y,
                                '>=': lambda r, y: r >= y,
                                '>': lambda r, y: r > y}
        self.price = 0
        #print(self.result, type(result), self.condition_for_price, type(self.condition_for_price))

    def prepare_named_result(self, recipient_name): # результат по литере
        if type(self.result) == str:
            comp_result = self.result.split(',')
            for i in comp_result:
                if i[0].isupper():
                    if i[0] == recipient_name[0]:
                        if len(i) == 1:
                            self.result = True
                        else:
                            self.result = float(i[1:]) if i[1:].isdigit() else i[1:]
                        break
                    else:
                        self.result = 'zero'
        return self.result

    def prepare_result(self):
        if type(self.result) == str:
            if ':' in self.result:
                time = [int(i) for i in self.result.split(':')]
                time = datetime.time(*time)
                self.result = datetime.datetime.combine(self.date, time)
                if self.result.hour < 8:
                    self.result += datetime.timedelta(days=1)

            elif self.result not in self.condition_for_price:
                self.result = {self.result[0]: self.result[1:]}

        print(self.result)
        return self.result

    #def prepare_condition(self):
    #    if type(self.condition_for_price) == str:
    #        if '{' in self.condition_for_price:
    #            self.condition_for_price = eval(self.condition_for_price)
    #        print(self.condition_for_price)
    #    return self.condition_for_price

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
                    #print(self.result, comparison_value)

                    inner_condition = self.comparison_dict[comparison_operator](self.result, comparison_value)
                    if inner_condition:
                        if type(self.condition_for_price[k]) == int:
                            self.price = self.condition_for_price[k]
                        else:
                            if not delta:
                                if comparison_value > self.result:
                                    delta = (comparison_value - self.result).seconds / 60
                                else:
                                    delta = (self.result - comparison_value).seconds / 60
                            else:
                                delta = 60
                            divider = float(self.condition_for_price[k].replace('*', ''))
                            self.price += delta * divider
                            #print(delta)
                        #print(k, self.condition_for_price[k], inner_condition, self.price)
# limiting
                    self.price = 200 if self.price > 200 else self.price
        return self.price

    def get_price_if_result_is_dict(self):
        print(self.condition_for_price)
        key_extraction = list(self.result)[0]
        self.result = {'key': key_extraction, 'value': self.result[key_extraction]}
        d = self.condition_for_price[self.result['key']]
        self.price = [d[i] for i in d if self.result['value'] in i][0]
        return int(self.price)

    def get_price(self):
        self.prepare_result()
        #print(self.type_result)
        if type(self.result) == datetime.datetime:
            return self.get_price_if_datetime()

        elif type(self.result) == dict:
            return self.get_price_if_result_is_dict()

        elif type(self.condition_for_price) == dict:
            print(self.result, type(self.result))
            if list(filter(lambda i: type(i) == str, self.condition_for_price.keys())):
                self.price = int(self.condition_for_price[self.result])
            return self.price

        if '*' in self.condition_for_price:
            divider = int(self.condition_for_price.replace('*', ''))
            self.price = divider * self.result
        else:
            self.price = int(self.condition_for_price)

        return self.price

#results = ['2', 1.0, 1, True, 'L1', 'L22:00', 'E1,L2', 'L']
#
#for i in results:
#    cc = ComplexCondition(result=i)
#    cc.prepare_named_result('Egr')
#    print(cc.result)
#    print()

#cc = ComplexCondition('+F', '{"+": {"CDIF": 50, "P": 0}, "-": {"CDIF": 0, "P": -50}}')
#cc = ComplexCondition('{<.22: 3*, <.23: 2*, >.23: 0}', '23,00')
#cc = ComplexCondition(result=True)
cc = ComplexCondition(True, '{"9": 50, "True": 0}')
print(cc.get_price())


