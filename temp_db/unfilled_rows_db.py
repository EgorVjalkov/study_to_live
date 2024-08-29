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

    def get_table(self,
                  with_dates: bool,
                  index_col: Optional[str] = None,
                  columns: Optional[list] = None) -> pd.DataFrame:
        table = pd.read_sql_table(self.table_name,
                                  con=engine,
                                  schema='public',
                                  index_col=index_col,
                                  columns=columns)
        if with_dates:
            table['DATE'] = table['DATE'].map(lambda i: i.date())
        return table

    def update_table(self, table: pd.DataFrame):
        table.to_sql(self.table_name,
                     con=engine,
                     if_exists='replace',
                     index_label='DATE')

    def get_day_row(self, date: datetime.date) -> pd.Series:
        table = self.get_table(with_dates=True).set_index('DATE')
        return table.loc[date]

    def set_day_row_and_upload(self, day_row: pd.Series): #-> None:
        table = self.get_table(with_dates=True).set_index('DATE')
        table.loc[day_row.name] = day_row
        self.update_table(table)
        return table


if __name__ == '__main__':

    month = 'aug24'
    path_to_excel = f'{month}.xlsx'

    vedomost = f'{month}_vedomost'
    price = f'{month}_price'
    coefs = 'coefs'

    ved_frame = pd.read_excel(path_to_excel, sheet_name='vedomost', index_col=0, dtype=str)
    print(ved_frame)
    df = DataBase(vedomost)
    #df.update_table(ved_frame)

    df = df.get_table(with_dates=True, index_col='DATE')
    print(df)
