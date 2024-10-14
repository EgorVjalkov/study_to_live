import datetime

import pandas as pd

from database.filter_recipes import set_filter
from database.database import DataBase
from filler.date_funcs import today_for_filling, get_month, get_dates_list, tomorrow


DATE_INTERVAL = 7


class BusyError(BaseException):
    pass


class Mirror:
    def __init__(self):
        self.status_series: pd.Series = pd.Series(dtype=object)
        self.date_of_last_update: datetime.date = today_for_filling()

    def __repr__(self):
        if self.status_series.empty:
            return 'Mirror(empty)'
        else:
            return (f'Mirror:'
                    f'{self.status_series}')

    @property
    def date(self):
        return self.date_of_last_update

    @date.setter
    def date(self, date: datetime.date):
        self.date_of_last_update = date

    @property
    def date_interval(self):
        return get_dates_list(self.date, before=-DATE_INTERVAL, after=DATE_INTERVAL)

    @property
    def series(self) -> pd.Series:
        return self.status_series

    @series.setter
    def series(self, series: pd.Series):
        self.status_series = series

    @staticmethod
    def get_vedomost_table_name(date: datetime.date):
        return f'{get_month(date)}_vedomost'

    @staticmethod
    def get_prices_table_name(date: datetime.date):
        return f'{get_month(date)}_price'

    def init_series(self) -> object:
        dates_list = self.date_interval

        ved_names = set()
        for date in dates_list[0],dates_list[-1]:
            ved_names.add(self.get_vedomost_table_name(date))

        for tab_name in ved_names:
            df = DataBase(tab_name).get_table(with_dates=True, columns=['DATE', 'STATUS'])
            self.series = pd.concat([self.series, df.set_index('DATE')['STATUS']], axis=0)

        self.series = self.series[dates_list]
        #print('after_init', self.series.index)

        return self

    def update_by_date(self, date: datetime.date) -> object:
        self.date = date
        interval = self.date_interval

        last_day_of_series = tomorrow(self.series.index[-1])
        delta = interval[-1].day - last_day_of_series.day

        dates_for_add = get_dates_list(last_day_of_series, after=delta)
        dates_ser = pd.Series({i: 'empty' for i in dates_for_add})

        status_series = pd.concat([self.series, dates_ser], axis=0)
        self.series = status_series[interval]
        #print('after_update', self.series.index)
        return self

    @property
    def mirror_df(self) -> pd.DataFrame:
        return pd.DataFrame({'DATE': self.status_series.index,
                             'STATUS': self.status_series.values})

    def get_dates_for(self, recipient: str, by_behavior: str) -> pd.Series:
        days_df = self.mirror_df.copy()
        if by_behavior != 'coefs':
            recipe = set_filter(self.date, recipient, by_behavior)
            for col_name in recipe:
                filter_ = recipe[col_name]
                filtered = days_df[col_name].map(filter_)
                days_df = days_df.loc[filtered == True]
        #print(days_df)
        print(f'get_dates_for_{recipient}_by_{by_behavior}_in_{self.date}')
        return days_df['DATE']

    def get_vedomost(self, date: datetime.date):
        ved_name = self.get_vedomost_table_name(date)
        return DataBase(ved_name).get_table(with_dates=True).set_index('DATE')

    def get_day_row(self, date: datetime.date):
        ved_name = self.get_vedomost_table_name(date)
        return DataBase(ved_name).get_day_row(date)

    def get_cells_data(self, behavior: str, date: datetime.date) -> pd.DataFrame:
        if behavior == 'coefs':
            return DataBase('coefs_data').get_table(with_dates=False, index_col='coef')
        else:
            table_name = self.get_prices_table_name(date)
            return DataBase(table_name).get_table(with_dates=False, index_col='category')

    def update_vedomost(self, day_row: pd.Series):
        vedomost = DataBase(self.get_vedomost_table_name(day_row.name))
        frame = vedomost.get_table(with_dates=True).set_index('DATE')
        frame.loc[day_row.name] = day_row
        vedomost.update_table(frame)
        print('не равен, запись, update')

    def check_date(self, date: datetime.date) -> None:
        day_status = self.series.get(date)
        if day_status == 'busy':
            raise BusyError

    def occupy(self, date: datetime.date) -> object:
        self.series[date] = 'busy'
        return self

    def set_day_status(self, day: pd.Series) -> object:
        self.series[day.name] = day.STATUS
        return self
