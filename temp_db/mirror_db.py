import datetime
from typing import Optional

import pandas as pd

from temp_db.recipes import set_filter
from temp_db.unfilled_rows_db import DataBase
from filler.date_funcs import today_for_filling, get_month
from filler.day_row import DayRow


class BusyError(BaseException):
    pass


class Mirror:
    def __init__(self):
        self.mirror_df: Optional[pd.DataFrame] = None
        self.date_of_last_update: datetime.date = today_for_filling()

    def __repr__(self):
        if self.mirror_df.empty:
            return 'Mirror(empty)'
        else:
            return (f'Mirror:'
                    f'{self.mirror_df}')

    @property
    def df(self) -> pd.DataFrame:
        return self.mirror_df

    @df.setter
    def df(self, data_frame: pd.DataFrame):
        self.mirror_df = data_frame

    @property
    def status_series(self) -> pd.Series:
        return self.mirror_df.set_index('DATE')['STATUS']

    #@status_series.setter
    #def status_series(self, series):
    #    self.mirror_df['STATUS'] =



    @property
    def date(self):
        return self.date_of_last_update

    @date.setter
    def date(self, date: datetime.date):
        self.date_of_last_update = date

    @property
    def vedomost_table_name(self):
        return f'{get_month(self.date_of_last_update)}_vedomost'

    @property
    def prices_table_name(self):
        return f'{get_month(self.date_of_last_update)}_price'

    def init_frame(self) -> object:
        self.df = DataBase(self.vedomost_table_name).get_table(with_dates=True, columns=['DATE', 'STATUS'])
        return self

    def get_day_row(self, date: datetime.date):
        return DataBase(self.vedomost_table_name).get_day_row(date)

    def get_prices(self):
        return DataBase(self.prices_table_name).get_table(with_dates=False)

    def check_date(self, date: datetime.date) -> None:
        day_status = self.df.set_index('DATE')['STATUS'].get(date)
        if day_status == 'busy':
            raise BusyError

    def occupy(self, date: datetime.date) -> object:
        self.df[date] = 'busy'
        return self

    def release(self, day: DayRow) -> object:
        self.mirror_df[day.date] = day.mark
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
        recipe = set_filter(self.date_of_last_update, recipient, by_behavior)
        days_df = self.mirror_df.copy()
        for col_name in recipe:
            filter_ = recipe[col_name]
            filtered = days_df[col_name].map(filter_)
            days_df = days_df.loc[filtered == True]
        print(f'get_dates_for_{recipient}_by_{by_behavior}')
        return days_df['DATE']
