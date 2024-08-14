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

    db = DataBase('aug24_vedomost')
    day_row = db.get_day_row(datetime.date.today())
    day_row['l:velo'] = '4'
    print(day_row)
    db.set_day_row_and_upload(day_row)
    df = db.get_table(with_dates=True)
    print(df)


#df = DataBase('aug24_prices').get_table(with_dates=False)

#get-set vedomost