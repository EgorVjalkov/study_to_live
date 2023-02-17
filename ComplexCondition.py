import datetime

class ComplexCondition:
    def __init__(self,  condition_for_price, result=0, date=''):
        self.result = result
        self.type_result = type(result)
        self.condition_for_price = condition_for_price
        self.date = datetime.date.today() if date == 'DATE' or not date else date
        self.comparison_dict = {'<': lambda r, y: r < y,
                                '<=': lambda r, y: r <= y,
                                '>=': lambda r, y: r >= y,
                                '>': lambda r, y: r > y}
        self.price = 0

    def prepare_result(self):
        if self.type_result == str:
            if ',' in self.result:
                time = [int(i) for i in self.result.split(',')]
                time = datetime.time(*time)
                self.result = datetime.datetime.combine(self.date, time)
                if self.result.hour < 8:
                    self.result += datetime.timedelta(days=1)

            elif self.result[0].isupper():
                self.result = {'key': self.result[1], 'value': self.result[0]}

            # elif self.result.isdigit():
            #     print(self.result)
            #     self.result = int(self.result)

        self.type_result = type(self.result)
        # print(self.type_result)

        return self.result, self.type_result

    def prepare_condition(self):
        if type(self.condition_for_price) == str:
            self.condition_for_price = eval(self.condition_for_price)
            #print(self.condition_for_price)
        return self.condition_for_price

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
                        if '*' in self.condition_for_price[k]:
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
                        else:
                            self.price += int(self.condition_for_price[k])
                        #print(k, self.condition_for_price[k], inner_condition, self.price)
# limiting
                    self.price = 200 if self.price > 200 else self.price
        return int(self.price)

    def get_price_if_result_is_dict(self):
        #print(self.condition_for_price)
        d = self.condition_for_price[self.result['key']]
        self.price = [d[i] for i in d if self.result['value'] in i][0]
        return int(self.price)

    def get_price(self):
        self.prepare_result()
        self.prepare_condition()

        if self.type_result == datetime.datetime:
            return self.get_price_if_datetime()
        elif self.type_result == dict:
            return self.get_price_if_result_is_dict()
        elif type(self.condition_for_price) == dict:
            self.price = int(self.condition_for_price[str(self.result)])
            return self.price

        if '*' in self.condition_for_price:
            divider = int(self.condition_for_price.replace('*', ''))
            self.price = divider * self.result
        else:
            self.price = int(self.condition_for_price)

        return self.price


cc = ComplexCondition('{"+": {"CDIF": 50, "P": 0}, "-": {"CDIF": 0, "P": -50}}', 'F+')
#cc = ComplexCondition('{<.22: 3*, <.23: 2*, >.23: 0}', '23,00')
#cc = ComplexCondition(4, '40*')
#cc.prepare_result()
#cc.prepare_condition_for_price()
print(cc.get_price())

