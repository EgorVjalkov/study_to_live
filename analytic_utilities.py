import pandas as pd
from statistics import mean


class FrameForAnalyse:
    def __init__(self, path='', df=pd.DataFrame()):
        if path:
            self.object = pd.read_excel(path)
        else:
            self.object = df.copy()

        self.axis = ''
        self.filtered_keys = []

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

    def get_frame_by_flag(self, with_statistic_flag=True):
        if not with_statistic_flag:
            self.df = self.df[:len(self.df)-2]
        return self.df

    def get_filter_func(self, _filter):
        return self.filters_dict[_filter]

    def get_axis_for_fltrtn(self, axis):
        axis_dict = {
            'index': self.object.index,
            'columns': self.object.columns
        }
        return axis_dict[axis]

    def filtration(self, _filters_d, axis='columns', filter_logic='pos', by_column=''):
        if by_column:
            self.axis = 'index'
            prefilter_dict = self.object[by_column].to_dict()
        else:
            self.axis = axis
            prefilter_dict = dict(enumerate(self.get_axis_for_fltrtn(axis)))

        for fltr in _filters_d:
            filter_func = self.get_filter_func(fltr)
            value = _filters_d[fltr]
            if value == 'mean':
                value = self.above_zero_mean(prefilter_dict)

            el_changer = lambda i: i if by_column else prefilter_dict[i]
            logic_dict = {'pos': [el_changer(i) for i in prefilter_dict if filter_func(prefilter_dict[i], value)],
                          'neg': [el_changer(i) for i in prefilter_dict if not filter_func(prefilter_dict[i], value)]}

            self.filtered_keys = logic_dict[filter_logic]
            print(self.filtered_keys)

        return self.object.filter(items=self.filtered_keys, axis=self.axis)

    def presentation_by_keys(self, other_df=pd.DataFrame()):
        if other_df.empty:
            return self.object.filter
        else:
            return other_df.filter(items=self.filtered_keys, axis=self.axis)

    def above_zero_mean(self, prefilter_d):
        values_above_zero = list(filter(lambda i: i >= 0, prefilter_d.values()))
        return round(mean(values_above_zero), 2)
