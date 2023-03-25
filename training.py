# from random import choice
# import pandas as pd
# import Classes as Cl
#
# d = {'1.12': False, '2.12': 5.9}
# d = pd.Series(d, name='A:GYM')
# x = {'1.12': True, '2.12': 2.9}
# x = pd.Series(x, name='A:BAD')
# y = {
#     d.name: d,
#     x.name: x
# }
# y = pd.DataFrame(y)
# print(y)
#
# month_data = pd.read_excel('months/dec22test/dec22.xlsx', sheet_name='vedomost').fillna(0)
# price_data = pd.read_excel('months/dec22test/dec22.xlsx', sheet_name='price').fillna(0)
#
# accessory_keys = ['DATE', 'DAY', 'DUTY', 'MOD', 'WEAK']
# category_keys = [i for i in month_data if i not in accessory_keys]
#
# accessory_data = month_data[accessory_keys]
# for i in accessory_data:
#     if accessory_data[i].dtypes == 'float':
#         print(i, True)
#         accessory_data[i] = accessory_data[i].astype(int)
# category_data = month_data[category_keys]
#
# print(category_data)
# print(accessory_data)
# print(price_data)
#
# post_count_dataframe = accessory_data
#
#
# class Lesson:
#     def __init__(self, count, consist, difficulty):
#         pass
#
# ABC = list('qwertyuiopasdfghjklzxcvbnm')
# special = list('()[]{}\'"\?:;-_=+!@#$%^&*/|')
# numbers = list('1234567890')
#
# all_marks = ABC + special + numbers
#print(all_marks)
#
# def new_test(num):
#     test_list = []
#     for i in range(num):
#         mark = choice(all_marks)
#         test_list.append(mark)
#     lesson = ' '.join(test_list)
#     if input('  ' + lesson + '\n: ') == lesson:
#         print('correct')
#     else:
#         print('mistakes')
#
# new_test(250)
list = {'Egr': 1, "Lrea": 2, 'adidas': 4}
iter = iter(list)
def change(iter):
    active = (next(iter))
    return active

active = change(iter)
print(active)
active = change(iter)
print(active)