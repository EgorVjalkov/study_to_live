import datetime
from typing import Optional
import os

import pandas as pd
from sqlalchemy import Engine

from temp_db.recipes import set_filter
from temp_db.unfilled_rows_db import MonthDB
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
    def need_update(self):
        return self.date_of_last_update < today_for_filling()

    def update_mirror_from_mf(self) -> object:
        table_name = f'{get_month(self.date_of_last_update)}_vedomost'
        self.mirror_df = pd.read_sql_table(table_name,
                                           con=self.engine,
                                           schema='public',
                                           columns=['DATE', 'STATUS'])
        self.mirror_df['DATE'] = self.mirror_df['DATE'].map(lambda i: i.date())
        return self

    def update_by_date(self) -> object:
        t = today_for_filling()
        delta = t - self.date_of_last_update
        for day in range(1, delta.days+1):
            date = self.date_of_last_update + datetime.timedelta(days=day)
            done = 'empty'
            self.mirror_df = pd.concat(
                [self.mirror_df,
                 pd.Series({date: done})]).sort_index()
        self.date_of_last_update = t
        return self

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
        return days_df.set_index('DATE')['STATUS']

    # сделай рефактор!!!
    def get_days_for_coef_correction(self, mode) -> pd.Series:
        series_list = []
        t = today_for_filling()
        if mode == 'coefs':
            day_dict = get_dates_list(t, 7, 7)
        else:
            day_dict = get_dates_list(t, 7, 0)

        if is_same_months(day_dict):
            print(is_same_months(day_dict))
            return self.series

        else:
            for day in day_dict:
                try:
                    mdb = MonthDB(self.path_to.months_temp_db_by(day_dict[day]),
                                  self.path_to.mother_frame_by(day_dict[day]))

                    mf = mdb.mf_from_file

                    if day == 's':
                        days_status = mf[mf.index >= day_dict[day]]['STATUS']
                    else:
                        days_status = mf[mf.index <= day_dict[day]]['STATUS']

                    if self.temp_db_exists(mdb.path_to_temp_db):
                        status_from_temp = mdb.temp_db_from_file['STATUS']
                        for date in days_status.index:
                            if date in status_from_temp.index:
                                days_status[date] = status_from_temp.at[date]

                    series_list.append(days_status)

                except FileNotFoundError:
                    print(f'vedomost of {day} is not exist')

        return self.concat_series(series_list)

    def update_db(self, day: DayRow) -> object:
        paths = self.get_paths_by(day.date)
        temp_db = MonthDB(*paths)

        if day.is_filled or day.is_empty:
            data_type = 'mf'
            if day.is_filled:
                temp_db.del_filled_row(day.date)
                self.mirror_df = self.mirror_df[self.mirror_df.index != day.date]  # <- рескан серии после удаления

        else:
            data_type = 'temp_db'
            self.mirror_df.at[day.date] = day.mark

        print(f'SAVE: {day.mark} --> {data_type}')
        frame = temp_db.load_as_(data_type)
        frame.loc[day.date] = day.row

        if day.is_filled:
            frame.loc[day.date] = frame.loc[day.date].fillna('can`t')

        temp_db.save_(frame, as_=data_type, mode='a')

        return self

    def load_prices_by(self, date: datetime.date, for_: str):
        path = self.path_to.mother_frame_by(date)
        sheet_name = for_ if for_ == 'coefs' else 'price'
        return pd.read_excel(path, sheet_name=sheet_name, index_col=0)
