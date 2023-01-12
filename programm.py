from Classes import MonthData, Day, CategoryPrice


month_data = MonthData('months/dec22test/dec22.xlsx')
# print(month_data.vedomost)
# print(month_data.prices)
for day in month_data.vedomost:
    day_data = Day(day)
    for i in day_data.categories:
        print('!!!!!!!', day_data.date, 'duty', day_data.duty, day_data.mods)
        category = CategoryPrice(i, day_data.categories[i], day_data.mods, day_data.duty, month_data.prices)
        bag = category.total_count_and_save_in_dict()
        containers = day_data.sort_to_containers(bag)
        print(containers, '\n')
    month_data.collect_all_in_month(containers)
month_data.add_longbox_money(600, 100)

print(month_data.egr_count, month_data.egr_meals, month_data.lera_count, month_data.lera_meals)





