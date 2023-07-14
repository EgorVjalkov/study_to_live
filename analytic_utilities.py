import pandas as pd
import pandas.core.frame
# доработай. функция должна возрващать какую-то область, хоть индекс, хоть категорию
# декларируй ф для фильтрации


class Filtered:
    def __init__(self, iter_object):
        self.object = iter_object

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

    def column_filter(self, filter_logic='positive', full_names=(), positions=(), name_part=''):
        prefilter = self.object.copy()
        if full_names:
            filtered = [prefilter.pop(i) for i in prefilter if i in full_names]
        elif positions:
            filtered = [prefilter.pop(i) for i in prefilter if i[0] in positions]
        elif name_part:
            filtered = [prefilter.pop(i) for i in prefilter if name_part in i]
        else:
            filtered = prefilter

        if filter_logic == 'negative':
            filtered = prefilter

        if self.type == pandas.core.frame.DataFrame and type(filtered) == list:
            filtered = {i.name: i for i in filtered}
            filtered = pd.DataFrame(filtered)

        return filtered

    def index_filter(self, column_n_name, comparison_func, _filter='mean', with_statistic=False):
        column_n = pd.Series(self.object[column_n_name].to_dict())
        if with_statistic:
            column_n = column_n.head(len(column_n)-2)
        if _filter == 'mean':
            _filter = round(column_n.mean(), 2)
        column_n_dict = column_n.to_dict()
        true_index = [i for i in column_n_dict if comparison_func(column_n_dict[i], _filter)]
        return true_index

