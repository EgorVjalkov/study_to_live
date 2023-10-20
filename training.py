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
import classes as cl


recipients = ['Egr', 'Lera']
month = "may23"
path_to_file_may = f'months/{month}/{month}.xlsx'
month_2 = "jun23NEW_VERSION"
path_to_file_jun = f'months/{month_2}/{month_2}.xlsx'
show_calc = True


month_data_may = cl.MonthData(path_to_file_may, recipients)
ad = cl.AccessoryData(month_data_may.accessory, month_data_may.mother_frame, recipients)
#ad.get_in_time_sleeptime_col('Egr', month_data.vedomost)
ad.get_mods_frame()
acc = pd.concat([month_data_may.date, ad.mods_frame], axis=1)
acc.to_excel(f'output_files/{month}/testing_af.xlsx')
cat = 'e:dev'
cf = cl.CategoryData('Egr', month_data_may.mother_frame[cat], ad.mods_frame, month_data_may.prices)
cf.add_price_column()
jun_prices = cl.MonthData(path_to_file_jun, recipients).prices[cat]
bonus_column = cl.BonusFrame(cf.cat_frame, jun_prices)
if bonus_column.bonus_logic():
    cf.cat_frame['bonus'] = bonus_column.count_a_bonus()
    print(cf.cat_frame.get(['mark', 'bonus']))

