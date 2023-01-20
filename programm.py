from Classes import MonthData, Day, CategoryData
import pandas as pd


pd.set_option('display.max.columns', None)


month_data = MonthData('months/dec22test/dec22.xlsx')
print(month_data.vedomost_like_df)

category_df = month_data.vedomost_like_df[month_data.category_keys]
accessory_df = month_data.vedomost_like_df[month_data.accessory_keys]

for i in category_df:
    category = CategoryData(category_df[i], accessory_df, month_data.prices_like_df)
    #print(category.price)
    category.find_a_price_and_save()
    month_data.add_a_column(category.name, '_price', category.category_price)
    month_data.add_a_column(category.name, '_coef', category.category_coefficients)

    # category = pd.Series(category_df[i].to_list(), index=month_data.vedomost_like_df['DATE'].astype('str'))

    category_data = category_df[i]
    category_data.to_list()

    # print(category_price)
columns = [i for i in month_data.vedomost_like_df if 'L:' in i]
print(month_data.vedomost_like_df[columns])
# print(month_data.prices)
# for day in month_data.vedomost:
#     day_data = Day(day)
#     for i in day_data.categories:
#         print('!!!!!!!', day_data.date, 'duty', day_data.duty, day_data.mods)
#         category = CategoryPrice(i, day_data.categories[i], day_data.mods, day_data.duty, month_data.prices)
#         bag = category.total_count_and_save_in_dict()
#         containers = day_data.sort_to_containers(bag)
#         print(containers, '\n')
#     month_data.collect_all_in_month(containers)
# month_data.add_longbox_money(600, 100)
#
# print(month_data.egr_count, month_data.egr_meals, month_data.lera_count, month_data.lera_meals)





