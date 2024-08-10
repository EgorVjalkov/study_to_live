from PriceMarkCalc import PriceMarkCalc


class CompCoef:
    def __init__(self, coef_data):
        self.coef_data: str = coef_data

    def __repr__(self):
        return f'CompCoef(coef_data={self.coef_data})'

    @property
    def severity_dict(self):
        name = self.coef_data[:self.coef_data.find('(')]
        severity = self.coef_data[self.coef_data.find('(')+1:self.coef_data.find(')')]
        #print(severity)
        return {'name': name, 'sev': severity}

    @property
    def have_coef_data(self):
        return True if self.coef_data else False

    def count_a_coef_value(self, coef, mark=''):
        counted_coef = self.coef_data
        if '{' in self.coef_data:
            counted_coef = eval(self.coef_data)[mark]
        elif '[' in self.coef_data:
            counted_coef = eval(self.coef_data)[int(coef)]

        if '*' in counted_coef:
            coef_value = PriceMarkCalc(coef).get_price_if_multiply(counted_coef)
            # print('value', coef_value)
            return coef_value
        else:
            # print('no multy', counted_coef)
            return float(counted_coef)

