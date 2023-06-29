import datetime
from random import choice

class PriceMarkCalc:
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
        self.condition = condition
        self.price = 0

        self.mark = result
        self.mark_dict = {'+': 'True', '-': 'False', '0': 'False'}

        self.date = datetime.date.today() if date == 'DATE' or not date else date

        # print(self.result, type(result), self.condition_for_price, type(self.condition_for_price))

    def prepare_result(self):
        if ':' in self.result:
            time = [int(i) for i in self.result.split(':')]
            time = datetime.time(*time)
            self.result = datetime.datetime.combine(self.date, time)
            if self.result.hour < 8:
                self.result += datetime.timedelta(days=1)

        else:
            if self.result not in self.condition:
                try:
                    self.result = float(self.result)
                except ValueError:
                    return self.result

        return self.result

    def get_price_if_datetime(self):
        delta = 0
        for k in self.condition:
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
                        if type(self.condition[k]) == int:
                            self.price += self.condition[k]
                        else:
                            if not delta:
                                if comparison_value > self.result:
                                    delta = (comparison_value - self.result).seconds / 60
                                else:
                                    delta = (self.result - comparison_value).seconds / 60
                            else:
                                delta = 60
                            multiplic = float(self.condition[k].replace('*', ''))
                            self.price += delta * multiplic
                            #print(delta)
                        #print(k, self.condition[k], inner_condition, self.price, '\n')
# limiting
                    self.price = 200 if self.price > 200 else self.price
        return self.price

    def get_price_if_comparison_logic(self):
        for i in self.condition:
            if '.' in i:
                operator, value = tuple(i.split('.'))
                if self.comparison_dict[operator](float(self.result), int(value)):
                    self.price = self.condition[i]
                    break
        return self.price

    def get_price_if_multiply(self, condition):
        multiplicator = float(condition.replace('*', ''))
        self.price = float(self.result) * multiplicator
        return self.price

    def get_price_if_complex_result(self):
        key, value = self.result[0], self.result[1:]
        result_d_by_key = self.condition[key]
        for i in result_d_by_key:
            if value in i:
                self.price = float(result_d_by_key[i])
        self.mark = key
        return self.price, self.mark

    def get_price(self):
        self.prepare_result()
        print(self.result, self.condition)

        if self.result in self.condition:
            self.price = self.condition[self.result]# done

        else:
            if self.comparison_flag:
                if type(self.result) == datetime.datetime:
                    self.get_price_if_datetime()
                else:
                    self.get_price_if_comparison_logic()# done

            else:
                self.get_price_if_complex_result()# done

        if '*' in str(self.price):
            self.price = self.get_price_if_multiply(self.price)# done

        if self.mark not in self.mark_dict:
            self.mark = 'True' if self.price >= 0 else 'False'
        else:
            self.mark = self.mark_dict[self.mark]

        return self.price, self.mark

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
                        self.result = 'wishn`t'
        return self.result


#results = ['2', 1.0, 1, True, 'L1', 'L22:00', 'E1,L2', 'L']

# for i in results:
#    cc = PriceMarkCalc(result=i)
#    cc.prepare_named_result('Egr')
#    print(cc.result)
#    print()

# cc = PriceMarkCalc('+F', '{"+": {"CDIF": 50, "P": 0}, "-": {"CDIF": 0, "P": -50}}')
cc = PriceMarkCalc('21:40', '{"<.22": "1.5*", "<.23": "0", ">.23": "-2*"}')
# cc = PriceMarkCalc(4.0, '10*')
# cc = PriceMarkCalc('1', '{1: 50, 0: 0}')
# cc = PriceMarkCalc(result=True)
# cc = PriceMarkCalc(4.0, '{">=.4": 50, "<.4": 0}')
print(cc.get_price())


