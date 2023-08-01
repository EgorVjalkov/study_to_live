import pandas as pd
from statistics import mean


class FrameForAnalyse:
    def __init__(self, path='', df=pd.DataFrame()):
        if path:
            self.father_object = pd.read_excel(path)
        else:
            self.father_object = df

        self.object = self.father_object.copy()
        # self.object['DATE'] = self.object['DATE'].convert_dtypes('str')
        # print(self.object['DATE'].dtypes)
        self.axis = 'columns'
        self.items = []
        self.date = ['DATE', 'DAY']
        self.cat_statistic = len(self.father_object) - 2
        self.row_statistic = ['day_sum', 'sleep_in_time', 'day_sum_in_time']

    @property
    def df(self):
        return self.object

    @df.setter
    def df(self, modified_df):
        self.object = modified_df

    @property
    def filters_dict(self):
        return {'<': lambda i, fltr: i < fltr,
                '<=': lambda i, fltr: i <= fltr,
                '>=': lambda i, fltr: i >= fltr,
                '>': lambda i, fltr: i > fltr,
                'part': lambda i, prt: prt in i,
                'columns': lambda i, clmns: i in clmns,
                'positions': lambda i, pos: i[0] in pos
                }

    def extract_statistic(self, behavior=('date', 'cat', 'row')):
        for i in behavior:
            if i == 'date':
                self.date, self.df = self.df[self.date], self.df[[i for i in self.df if i not in self.date]]
            if i == 'cat':
                self.cat_statistic, self.df = self.df[self.cat_statistic:], self.df[:self.cat_statistic]
            if i == 'row':
                self.row_statistic, self.df = (
                    self.df[self.row_statistic], self.df[[i for i in self.df if i not in self.row_statistic]])
        return self.df, self.cat_statistic, self.row_statistic


    def get_items_by_axis(self):
        axis_dict = {
            'index': self.father_object.index,
            'columns': self.father_object.columns
        }
        return axis_dict[self.axis]

    def get_filter_func(self, _filter):
        return self.filters_dict[_filter]

    def behavior(self, by_column='', by_row=0):
        pass

    def filtration(self, _filters_d, by_column='', by_row=0, filter_logic='pos'):
        if by_column:
            self.axis = 'index'
            prefilter_dict = self.object[by_column].to_dict()
        elif by_row:
            self.axis = 'columns'
            prefilter_dict = self.object[by_row:by_row+1].to_dict('row')[0]
        else:
            prefilter_dict = dict(enumerate(self.get_items_by_axis()))

        for fltr in _filters_d:
            filter_func = self.get_filter_func(fltr)
            value = _filters_d[fltr]
            if value == 'mean':
                value = self.above_zero_mean(prefilter_dict)

            el_changer = lambda i: i if any((by_column, by_row)) else prefilter_dict[i]
            logic_dict = {'pos': [el_changer(i) for i in prefilter_dict if filter_func(prefilter_dict[i], value)],
                          'neg': [el_changer(i) for i in prefilter_dict if not filter_func(prefilter_dict[i], value)]}

            self.items = logic_dict[filter_logic]

        return self.df.filter(items=self.items, axis=self.axis)

    def presentation_by_keys(self, other_df):
        return other_df.filter(items=self.items, axis=self.axis)

    def above_zero_mean(self, prefilter_d):
        values_above_zero = list(filter(lambda i: i >= 0, prefilter_d.values()))
        return round(mean(values_above_zero), 2)
