import pandas as pd
from statistics import mean


class FrameForAnalyse:
    def __init__(self, path='', df=pd.DataFrame()):
        if path:
            self.father_object = pd.read_excel(path).fillna('')
        else:
            self.father_object = df

        self.object = self.father_object.copy()
        # self.object['DATE'] = self.object['DATE'].convert_dtypes('str')
        # print(self.object['DATE'].dtypes)
        self.default_items = list(self.object.columns)

        self.date = ['DATE', 'DAY']
        self.cat_statistic = len(self.father_object) - 2
        self.row_statistic = ['day_sum', 'sleep_in_time', 'day_sum_in_time']
        self.extracted = []

    @property
    def df(self):
        return self.object

    @df.setter
    def df(self, modified_df):
        self.object = modified_df

    @property
    def filters_dict(self):
        return {'<': lambda i, fltr: int(i) < fltr,
                '<=': lambda i, fltr: int(i) <= fltr,
                '>=': lambda i, fltr: int(i) >= fltr,
                '>': lambda i, fltr: int(i) > fltr,
                '=': lambda i, fltr: i == fltr,
                'part': lambda i, prt: prt in i,
                'columns': lambda i, clmns: i in clmns,
                'positions': lambda i, pos: i[0] in pos
                }

    def get_filter_func(self, _filter):
        return self.filters_dict[_filter]

    @property
    def items(self):
        return self.default_items

    @items.setter
    def items(self, iter_object):
        self.default_items = iter_object

    def filtration(self, filters_list, stat_extr=()):
        if stat_extr:
            self.items, self.extracted = self.extract_statistic(stat_extr)
        for fltr in filters_list:
            dict_object = pd.Series(self.items).to_dict()
            fltr_type, value, filter_logic = fltr[0], fltr[1], fltr[2]
            filter_func = self.get_filter_func(fltr_type)
            if value == 'mean':
                value = self.above_zero_mean(dict_object)

            if filter_logic == 'pos':
                self.items = [i for i in dict_object if filter_func(dict_object[i], value)]
            elif filter_logic == 'neg':
                self.items = [i for i in dict_object if not filter_func(dict_object[i], value)]

            if type(self.items) == list:
                self.items = [dict_object[i] for i in self.items]

        return self.items

    def extract_statistic(self, behavior):
        if 'date' in behavior:
            self.filtration([('columns', self.date, 'neg')])
        if 'row' in behavior:
            self.filtration([('columns', self.row_statistic, 'neg')])
        if 'cat' in behavior:
            self.items = self.items[:self.cat_statistic]

        return self.items, self.extracted

    def above_zero_mean(self, prefilter_d):
        values_above_zero = list(filter(lambda i: i >= 0, prefilter_d.values()))
        return round(mean(values_above_zero), 2)
