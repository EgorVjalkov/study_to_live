import pandas as pd
import classes as cl
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
import pandas as pd

list = {'Egr': 1, "Lrea": 2, 'adidas': 4}
iter = iter(list)
def change(iter):
    active = (next(iter))
    return active

active = change(iter)
print(active)
active = change(iter)
print(active)


def check_dicts_in_price_frame(price_frame):
    turn_out_dict = lambda i: type(i) == str and '{' in i
    for cat in price_frame:
        if cat != 'category':
            cat_dict = pd.DataFrame(price_frame[cat].to_list(), index=price_frame['category'], columns=[cat])
            cat_dict = cat_dict.to_dict('index')
            #print(cat_dict)
            for index in cat_dict:
                value = cat_dict[index][cat]
                #print(index, value)
                if turn_out_dict(value):
                    try:
                        check = eval(value)
                    except SyntaxError:
                        print(cat, index, value)
                    else:
                        print(f"all data is correct in {cat}")

month = "m23"
path_to_file = f'months/{month}/{month}.xlsx'
prices = pd.read_excel(path_to_file, sheet_name='price')
check_dicts_in_price_frame(prices)
