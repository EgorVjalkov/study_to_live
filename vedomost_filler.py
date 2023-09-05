import pandas as pd
import datetime
import classes as cl


MONTH = 'sep23'
recipients = ['Egr', 'Lera']

path_to_file = f'months/{MONTH}/{MONTH}.xlsx'

md = cl.MonthData(path_to_file)
md.get_frames_for_working(limiting='DATE')
for i in md.accessory['DUTY']:
    if pd.notna(i):
        print(type(i))
