import classes as cl
import os
import pandas as pd
from testing import does_need_correction


recipients = ['Egr', 'Lera']
month = "may23"

path_to_file = f'months/{month}/{month}.xlsx'
show_calc = True

if not does_need_correction(pd.read_excel(path_to_file, sheet_name='price')):

    while True:
        try:
            os.mkdir(f'output_files/{month}')
        except FileExistsError:
            break

    md = cl.MonthData(path_to_file, recipients)
    ad = cl.AccessoryData(md.accessory)
    ad.get_mods_frame()
    for name in recipients:
        while True:
            try:
                os.mkdir(f'output_files/{month}/{name}')
            except FileExistsError:
                break

        md.get_named_vedomost(name)
        #print(month_data.recipients)
        result_dict = {}
        for column in md.recipients[name]:
            if column.islower():
                #column = 'h:kitchen'
                cd = cl.CategoryData(name, md.recipients[name][column], ad.mods_frame, md.prices)
                cd.add_price_column(show_calculation=show_calc)
                cd.add_coef_and_result_column(show_calculation=show_calc)

                bonus_column = cl.BonusFrame(cd.cat_frame, cd.price_frame)
                if bonus_column.has_bonus_logic():
                    cd.cat_frame['bonus'] = bonus_column.count_a_bonus()
                    bl_with_sum = bonus_column.get_bonus_list_with_sum()
                else:
                    bl_with_sum = ()

                result_dict[column] = cd.cat_frame['result'].sum()
                #print(month_data.recipients[name])

                md.collect_to_result_frame(name, column, cd.cat_frame['result'], cd.count_true_percent(), bl_with_sum)
                cd.cat_frame = md.date.join(cd.cat_frame)
                cd.cat_frame = cd.cat_frame.set_index('DATE')
                cd.cat_frame.to_excel(f'output_files/{month}/{name}/{name}:{column}.xlsx', sheet_name=column.replace(':', '_'))
                #break
        print(name)
        md.result_frame[name].set_index('DATE').to_excel(f'output_files/{month}/{name}/{name}_total.xlsx', sheet_name='total')
        print(pd.Series(result_dict), pd.Series(result_dict).sum())
# здесь баги в тотале нужно искать проблемму