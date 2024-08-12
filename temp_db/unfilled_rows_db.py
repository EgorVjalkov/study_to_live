import datetime
from typing import Optional
from sqlalchemy import create_engine
import pandas as pd

from connection_config import user, password, host, db_name


engine = create_engine(
    f'postgresql+psycopg2://{user}:{password}@{host}:5432/{db_name}')


class DataBase:
    def __init__(self, table_name):
        self.table_name = table_name

    def get_table(self, with_dates: bool, columns: Optional[list] = None) -> pd.DataFrame:
        table = pd.read_sql_table(self.table_name,
                                  con=engine,
                                  schema='public',
                                  columns=columns)
        if with_dates:
            table['DATE'] = table['DATE'].map(lambda i: i.date())
        return table

    def set_table(self, table: pd.DataFrame) -> None:
        table.to_sql(self.table_name,
                     con=engine,
                     if_exists='replace',
                     index_label='DATE')

    def get_day_row(self, date: datetime.date) -> pd.Series:
        table = self.get_table(with_dates=True)
        return table.loc[date]


#get-set vedomost