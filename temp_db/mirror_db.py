import datetime
from typing import Optional
import os

import pandas as pd
from sqlalchemy import Engine

from temp_db.recipes import set_filter
from temp_db.unfilled_rows_db import DataBase
from filler.date_funcs import (today_for_filling, yesterday, week_before_, get_month,
                               last_date_of_past_month, get_dates_list, is_same_months)
from filler.day_row import DayRow


class Mirror:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.mirror_df: Optional[pd.DataFrame] = None
        self.date_of_last_update: datetime.date = today_for_filling()

    def __repr__(self):
        if self.mirror_df.empty:
            return 'Mirror(empty)'
        else:
            return (f'Mirror:'
                    f'{self.mirror_df}')

    @property
    def series(self) -> pd.Series:
        return self.mirror_df.set_index('DATE')['STATUS']

    @series.setter
    def series(self, series: pd.Series):
        self.mirror_df['STATUS'] = series

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

    def get_mirror_frame(self) -> object:
        return DataBase(self.vedomost_table_name).get_table(with_dates=True, columns=['DATE', 'STATUS'])

    def get_day_row(self, date: datetime.date):
        return DataBase(self.vedomost_table_name).get_day_row(date)

    def get_prices(self):
        return DataBase(self.prices_table_name).get_table(with_dates=False)

    def occupy(self, date: datetime.date) -> object:
        self.mirror_df[date] = 'busy'
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

