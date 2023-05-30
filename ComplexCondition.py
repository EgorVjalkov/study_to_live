import datetime
from random import choice

class ComplexCondition:
    def __init__(self, result='', condition='', date=''):
        self.comparison_dict = {'<': lambda r, y: r < y,
                                '<=': lambda r, y: r <= y,
                                '>=': lambda r, y: r >= y,
                                '>': lambda r, y: r > y}

        if '{' in condition:
            for operator in self.comparison_dict:
                if operator in condition:
                    self.comparison_flag = True
                    break
                else:
                    self.comparison_flag = False
            condition = eval(condition)

        self.result = result
        self.condition_for_price = condition
        self.price = 0

        self.date = datetime.date.today() if date == 'DATE' or not date else date

        # print(self.result, type(result), self.condition_for_price, type(self.condition_for_price))

    def prepare_result_if_condition_is_dict(self):
        if ':' in self.result:
            time = [int(i) for i in self.result.split(':')]
            time = datetime.time(*time)
            self.result = datetime.datetime.combine(self.date, time)
            if self.result.hour < 8:
                self.result += datetime.timedelta(days=1)

        else:
            if self.result not in self.condition_for_price:
                try:
                    if int(self.result) in self.condition_for_price:
                        self.result = int(self.result)
                except ValueError:
                    self.result = {self.result[0]: self.result[1:]}

        return self.result

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
                            multiplic = float(self.condition_for_price[k].replace('*', ''))
                            self.price += delta * multiplic
                            #print(delta)
                        #print(k, self.condition_for_price[k], inner_condition, self.price)
# limiting
                    self.price = 200 if self.price > 200 else self.price
        return self.price

    def get_price_if_comparison_logic(self):
        for i in self.condition_for_price:
            operator, value = tuple(i.split('.'))
            if self.comparison_dict[operator](int(self.result), int(value)):
                self.condition_for_price = self.condition_for_price[i]
                break
        if '*' in str(self.condition_for_price):
            self.price = self.get_price_if_multiply()
        else:
            self.price = int(self.condition_for_price)
        return self.price

    def get_price_if_multiply(self):
        multiplicator = int(self.condition_for_price.replace('*', ''))
        return float(self.result) * multiplicator

    def get_price_if_result_is_dict(self):
        key_extraction = list(self.result)[0]
        self.result = {'key': key_extraction, 'value': self.result[key_extraction]}
        d = self.condition_for_price[self.result['key']]
        self.price = [d[i] for i in d if self.result['value'] in i][0]
        return int(self.price)

    def get_price(self):
        if type(self.condition_for_price) == dict:
            self.prepare_result_if_condition_is_dict()

            if self.comparison_flag:
                if type(self.result) == datetime.datetime:
                    return self.get_price_if_datetime()
                else:
                    return self.get_price_if_comparison_logic()

            else:
                if type(self.result) == dict:
                    return self.get_price_if_result_is_dict()
                else:
                    self.price = self.condition_for_price[self.result]
        else:
            if '*' in str(self.condition_for_price):
                self.price = self.get_price_if_multiply()
            else:
                self.price = self.condition_for_price

        return int(self.price)

    def prepare_named_result(self, recipient_name): # результат по литере
        if type(self.result) == str:
            comp_result = self.result.split(',')
            for i in comp_result:
                if i[0].isupper():
                    if i[0] == recipient_name[0]:
                        if len(i) == 1:
                            self.result = 'True'
                        else:
                            self.result = i[1:] if i[1:].isdigit() else i[1:]
                        break
                    else:
                        self.result = 'zero'
        return self.result


#results = ['2', 1.0, 1, True, 'L1', 'L22:00', 'E1,L2', 'L']
#
#for i in results:
#    cc = ComplexCondition(result=i)
#    cc.prepare_named_result('Egr')
#    print(cc.result)
#    print()

# cc = ComplexCondition('+F', '{"+": {"CDIF": 50, "P": 0}, "-": {"CDIF": 0, "P": -50}}')
# cc = ComplexCondition('23:00', '{"<.22": "3*", "<.23": "2*", ">.23": 0}')
# cc = ComplexCondition(4.0, '10*')
cc = ComplexCondition('1', '{1: 50, 0: 0}')
# cc = ComplexCondition(result=True)
# cc = ComplexCondition(4.0, '{">=.4": 50, "<.4": 0}')
print(cc.get_price())


