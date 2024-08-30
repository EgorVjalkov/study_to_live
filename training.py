import datetime
import pandas as pd
from temp_db.unfilled_rows_db import DataBase

#
#for i in [1, 7, 20, 21]:
#    message_day = datetime.datetime.now()
#    #message_time = message_day.time()
#    message_time = datetime.time(hour=i, minute=0)
#    midnight = datetime.time(hour=0, minute=0)
#    if message_time.hour in range(6, 21):
#        print()
#    else:
#        if message_time.hour in range(0, 6):
#            message_time = midnight
#            message_day -= datetime.timedelta(days=1)
#    message_day = datetime.date.strftime(message_day, '%d.%m.%y')
#
#    print(message_day, message_time)
#    print()

day_row = DataBase('aug24_vedomost').get_day_row(datetime.date.today())
time_in = datetime.datetime.now()

list_ind = [i for i in day_row.index if ':' in i]
pd_ind = pd.Index(list_ind)
#cats = day_row[pd_ind]

#new_index = day_row.index.map(lambda i: ':' in i)
#day_row = day_row.index[new_index == True]

time_out = datetime.datetime.now()
print(time_out-time_in)
print(day_row)


fool = '000025'
pd_ind = '001892'
list_ind = '002331'


