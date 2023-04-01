import classes as cl
import os
import pandas as pd
from testing import does_need_correction


recipients = ['Egr', 'Lera']
month = "m23"
path_to_file = f'months/{month}/{month}.xlsx'
show_calc = True

if not does_need_correction(pd.read_excel(path_to_file, sheet_name='price')):

    while True:
        try:
            os.mkdir(f'output_files/{month}')
        except FileExistsError:
            break

    month_data = cl.MonthData(path_to_file, recipients)
    ad = cl.AccessoryData(month_data.accessory)
    ad.get_mods_frame()
    for name in recipients:
        while True:
            try:
                os.mkdir(f'output_files/{month}/{name}')
            except FileExistsError:
                break

        month_data.get_named_vedomost(name)
        #print(month_data.recipients)
        result_dict = {}
        for column in month_data.recipients[name]:
            if column.islower():
                #column = 'a:bottle'
                cd = cl.CategoryData(name, month_data.recipients[name][column], ad.mods_frame, month_data.prices)
                cd.add_price_column(show_calculation=show_calc)
                cd.add_coef_and_result_column(show_calculation=show_calc)
                result_dict[column] = cd.cat_frame['result'].sum()
                month_data.collect_to_result_frame(name, column, cd.cat_frame['result'])
                cd.cat_frame = month_data.date.join(cd.cat_frame)
                cd.cat_frame = cd.cat_frame.set_index('DATE')
                cd.cat_frame.to_excel(f'output_files/{month}/{name}/{name}:{column}.xlsx', sheet_name=column.replace(':', '_'))
                #break
        print(name)
        month_data.result_frame[name].to_excel(f'output_files/{month}/{name}/{name}_total.xlsx', sheet_name='total')
        print(pd.Series(result_dict), pd.Series(result_dict).sum())

# сделай чтоб в таблицу total писала сумма