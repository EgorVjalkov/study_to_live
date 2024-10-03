import datetime
from typing import Optional

import pandas as pd

from temp_db.recipes import set_filter
from temp_db.unfilled_rows_db import DataBase
from filler.date_funcs import today_for_filling, get_month, get_dates_list, is_same_months


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
    def mirror_df(self) -> pd.DataFrame:
        index = range(len(self.series))
        date_ser = pd.Series(self.status_series.index, index=index, name='DATE')
        status_ser = pd.Series(self.status_series.values, index=index, name='STATUS')
        df = pd.concat([date_ser, status_ser], axis=1)
        return df

    @property
    def series(self) -> pd.Series:
        return self.status_series

    @series.setter
    def series(self, series: pd.Series):
        self.status_series = series

    @property
    def date(self):
        return self.date_of_last_update

    @date.setter
    def date(self, date: datetime.date):
        self.date_of_last_update = date

    @property
    def date_interval(self):
        return get_dates_list(self.date_of_last_update, before=-DATE_INTERVAL, after=DATE_INTERVAL)

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

        return self

    def update_by_date(self, date: datetime.date) -> object:
        self.date = date
        interval = self.date_interval
        delta = interval[-1].day - self.series.index[-1].day

        dates_for_add = get_dates_list(self.series.index[-1], after=delta)
        dates_for_add = dates_for_add[1:] # потому что этот день уже учитан в серии
        dates_ser = pd.Series({i: 'empty' for i in dates_for_add})
        print(dates_ser)

        self.series = pd.concat([self.series, dates_ser], axis=0)
        print(self.series)
        self.series = self.series[interval]
        return self

    def get_vedomost(self, date: datetime.date):
        ved_name = self.get_vedomost_table_name(date)
        return DataBase(ved_name).get_table(with_dates=True).set_index('DATE')

    def get_day_row(self, date: datetime.date):
        ved_name = self.get_vedomost_table_name(date)
        return DataBase(ved_name).get_day_row(date)
    # здесь нужно подумать, т.к. устроено все топорно. и работает лишь там где месяц соответствует!

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

    @staticmethod
    def concat_series(series_list: list) -> pd.Series | pd.DataFrame:
        if len(series_list) > 1:
            series = pd.concat(series_list)
        else:
            series = series_list[0]
        return series.sort_index()

    def get_dates_for(self, recipient: str, by_behavior: str) -> pd.Series:
        # это прекрасно выглядит, но подумай над подгрузкой других ведомостей
        recipe = set_filter(self.date, recipient, by_behavior)
        days_df = self.mirror_df.copy()
        for col_name in recipe:
            filter_ = recipe[col_name]
            filtered = days_df[col_name].map(filter_)
            print(filtered)
            days_df = days_df.loc[filtered == True]
        print(days_df)
        print(f'get_dates_for_{recipient}_by_{by_behavior}_in_{self.date}')
        return days_df['DATE']
