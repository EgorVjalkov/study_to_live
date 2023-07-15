import pandas as pd
import pandas.core.frame
# доработай. функция должна возрващать какую-то область, хоть индекс, хоть категорию
# декларируй ф для фильтрации


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
        column_n = pd.Series(self.object[column_n_name].to_dict())
        if value == 'mean':
            value = round(column_n.mean(), 2)
        column_n_dict = column_n.to_dict()
        filtered_keys = [i for i in column_n_dict if filter_func(i, value)]
        return filtered_keys

    def filtration(self, filter_in_str, value, axis='columns', filter_logic='pos', column_n_name=''):
        filter_func = self.get_filter_func(filter_in_str)
        if column_n_name:
            self.filtered_keys = self.filtration_by_column(column_n_name, filter_func, value)
        else:
            prefilter_keys = list(self.get_obj_axis(axis))
            print(prefilter_keys)
            # здесь проблемма
            filtered_keys = [prefilter_keys.pop(i) for i in prefilter_keys if filter_func(i, value)]
            logic_dict = {'pos': filtered_keys, 'neg': prefilter_keys}
            self.filtered_keys = logic_dict[filter_logic]
        return self.filtered_keys

    def presentation_by_keys(self, new_object=pd.DataFrame()):
        if not new_object.empty:
            return new_object.filter(items=self.filtered_keys)
        else:
            return self.object.filter(items=self.filtered_keys)
