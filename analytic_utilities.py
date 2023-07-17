import pandas as pd
from statistics import mean


class Filtered:
    def __init__(self, iter_object, with_statistic=False):
        self.object = iter_object.copy()
        if with_statistic:
            self.object = self.object.head(len(self.object)-2)
        self.filtered_keys = []

    @property
    def type(self):
        return type(self.object)

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

    def get_filter_func(self, filter_in_str):
        return self.filters_dict[filter_in_str]

    def get_obj_axis(self, axis):
        axis_dict = {
            'index': self.object.index,
            'columns': self.object.columns
        }
        return axis_dict[axis]

    def filtration_by_column(self, column_n_name, filter_func, value):
        column_n_dict = self.object[column_n_name].to_dict()
        print(column_n_dict)
        if value == 'mean':
            values_above_zero = list(filter(lambda i: i >= 0, column_n_dict.values()))
            value = round(mean(values_above_zero), 2)
            print(value)
            #value = mean(column_n_dict.values())
        filtered_keys = [i for i in column_n_dict if filter_func(column_n_dict[i], value)]
        print(filtered_keys)
        return filtered_keys

    def filtration(self, filter_in_str, value, axis='columns', filter_logic='pos', by_column=''):
        filter_func = self.get_filter_func(filter_in_str)
        if by_column:
            axis = 'index'
            self.filtered_keys = self.filtration_by_column(by_column, filter_func, value)
        else:
            prefilter_dict = dict(enumerate(self.get_obj_axis(axis)))
            logic_dict = {'pos': [prefilter_dict[i] for i in prefilter_dict if filter_func(prefilter_dict[i], value)],
                          'neg': [prefilter_dict[i] for i in prefilter_dict if not filter_func(prefilter_dict[i], value)]}
            self.filtered_keys = logic_dict[filter_logic]
        return self.object.filter(items=self.filtered_keys, axis=axis)

    def presentation_by_keys(self, new_object=pd.DataFrame()):
        return new_object.filter(items=self.filtered_keys)
