from random import choice
import pandas as pd


df = pd.read_excel('months/dec22test/dec22.xlsx', sheet_name='FOR_TEST').fillna(0)
print(df)
df = df.select_dtypes(include=['float64']).astype('int')
print(df)









class Lesson:
    def __init__(self, count, consist, difficulty):
        pass

values = [True, False, True, None, True]
print(['yes' if v is True else 'no' if v is False else 'unknown' for v in values])
# ['yes', 'no', 'yes', 'unknown', 'yes']

ABC = list('qwertyuiopasdfghjklzxcvbnm')
special = list('()[]{}\'"\?:;-_=+!@#$%^&*/|')
numbers = list('1234567890')

all_marks = ABC + special + numbers
print(all_marks)

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

new_test(250)
