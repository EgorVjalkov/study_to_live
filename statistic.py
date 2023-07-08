import pandas as pd
import pandas.core.frame


class InnerIterObject:
    def __init__(self, iter_object):
        self.object = iter_object

    @property
    def type(self):
        return type(self.object)

    def filter(self, filter_logic='positive', full_names=(), positions=(), name_part=''):
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
