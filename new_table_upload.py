import pandas as pd
from database.database import DataBase
from testing import does_need_correction

def vedomost_upload(dir_path: str, table_name: str, mode: str = 'save'):
    path_to_v = f'{dir_path}/{table_name}.xlsx'
    ved_frame = pd.read_excel(path_to_v, sheet_name='vedomost', index_col=0, dtype=str)
    if mode == 'probe':
        print(ved_frame)
        return
    df = DataBase(table_name)
    df.update_table(ved_frame, 'DATE')
    df = df.get_table(with_dates=True).set_index('DATE')
    print(df)

def price_upload(dir_path: str, table_name: str, mode: str = 'save'):
    path_to_p = f'{dir_path}/{table_name}.xlsx'
    price_frame = pd.read_excel(path_to_p, sheet_name='price', index_col=0, dtype=str)
    if mode == 'probe':
        print(price_frame)
        print("Does need correction: ", does_need_correction(price_frame))
        return
    if not does_need_correction(price_frame):
        db = DataBase(table_name)
        db.update_table(price_frame, 'category')
        df = db.get_table(with_dates=False, index_col='category')
        print(df)

def vedomost_download(month: str):
    table_name = f'{month}_vedomost'
    df = DataBase(table_name)
    df = df.get_table(with_dates=True).set_index('DATE')
    df.to_excel(f'{table_name}.xlsx')

def price_download(month: str):
    table_name = f'{month}_price'
    db = DataBase(table_name)
    df = db.get_table(with_dates=False, index_col='category')
    df.to_excel(f'{table_name}.xlsx')


if __name__ == '__main__':
    pd.set_option('display.max_columns', 100)
    month = 'jan25'
    path = f'months/{month}'

    # for vedomost download
    #vedomost_download('oct24')

    # for vedomost upload:

    #table_name = f'{month}_vedomost'
    #vedomost_upload(path, table_name,
    #                mode='probe',
    #                )

    # for price upload:
    #table_name = f'{month}_price'
    #price_upload(path, table_name,
    #             mode='probe',
    #             )

    # for price download
    price_download(month)

