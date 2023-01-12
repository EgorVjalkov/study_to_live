from random import choice
import pandas as pd
# import Classes as Cl

d = {'1.12': False, '2.12': 5.9}
d = pd.Series(d, name='A:GYM')
x = {'1.12': True, '2.12': 2.9}
x = pd.Series(x, name='A:BAD')
y = {
    d.name: d,
    x.name: x
}
y = pd.DataFrame(y)
# print(y)

month_data = pd.read_excel('months/dec22test/dec22.xlsx', sheet_name='vedomost').fillna(0)
price_data = pd.read_excel('months/dec22test/dec22.xlsx', sheet_name='price').fillna(0)
print(price_data)
date_series = month_data['DATE'].astype('str')
duty_series = [str(i) if i else False for i in month_data['DUTY'].astype('int').to_list()]

new_data = month_data[['DATE', 'DAY', 'DUTY', 'MOD', 'WEAK']]
for i in new_data:
    if new_data[i].dtypes == 'float':
        print(i, True)
        new_data[i] = new_data[i].astype(int)
print(month_data)
date_series = month_data['DATE'].astype('str')
duty_series = [str(i) if i else False for i in month_data['DUTY'].astype('int').to_list()]

new_data = month_data[['DATE', 'DAY']]
new_data = new_data.assign(DUTY=duty_series)
# print(duty_series)
print(new_data)

# Setting the new value
# data.loc[data.bidder == 'parakeet2004', 'bidderrate'] = 100
# Taking a look at the result
# data[data.bidder == 'parakeet2004']['bidderrate']

class Lesson:
    def __init__(self, count, consist, difficulty):
        pass

ABC = list('qwertyuiopasdfghjklzxcvbnm')
special = list('()[]{}\'"\?:;-_=+!@#$%^&*/|')
numbers = list('1234567890')

all_marks = ABC + special + numbers
# print(all_marks)

def new_test(num):
    test_list = []
    for i in range(num):
        mark = choice(all_marks)
        test_list.append(mark)
    lesson = ' '.join(test_list)
    if input('  ' + lesson + '\n: ') == lesson:
        print('correct')
    else:
        print('mistakes')

# new_test(250)
