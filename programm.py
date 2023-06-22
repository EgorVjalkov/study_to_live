import classes as cl
import os
import pandas as pd
from testing import does_need_correction


recipients = ['Egr', 'Lera']
month = "jun23NEW_VERSION"

path_to_file = f'months/{month}/jun23OLD_VERSION.xlsx'
show_calc = True

if not does_need_correction(pd.read_excel(path_to_file, sheet_name='price')):

    while True:
        try:
            os.mkdir(f'output_files/{month}')
        except FileExistsError:
            break

    md = cl.MonthData(path_to_file, recipients)
    ad = cl.AccessoryData(md.accessory, md.vedomost, recipients)
    ad.get_mods_frame()

    for name in recipients:
        while True:
            try:
                os.mkdir(f'output_files/{month}/{name}')
            except FileExistsError:
                break

        #for_self_control = ad.mods_frame.get(['positions', 'named_coefs'])
        #extract_by_name = lambda i: i[name]
        #for_self_control = for_self_control.applymap(extract_by_name)
        #for_self_control.to_excel(f'output_files/{month}/{name}_self_control_OLD.xlsx')

        md.get_named_vedomost(name)
        #print(for_self_control)
#        #print(month_data.recipients)
#        result_dict = {}
#        for column in md.recipients[name]:
#            if column.islower():
#                #column = 'e:plan'
#                cd = cl.CategoryData(name, md.recipients[name][column], ad.mods_frame, md.prices)
#                cd.add_price_column(show_calculation=show_calc)
#                cd.add_coef_and_result_column(show_calculation=show_calc)
#                result_dict[column] = cd.cat_frame['result'].sum()
#
#                bonus_column = cl.BonusFrame(cd.cat_frame, cd.price_frame)
#                if bonus_column.has_bonus_logic():
#                    cd.cat_frame['bonus'] = bonus_column.count_a_bonus()
#                    result_dict[column+'_bonus'] = cd.cat_frame['bonus'].sum()
#                    bc_with_sum = bonus_column.get_bonus_list_with_sum()
#                else:
#                    bc_with_sum = ()
#
#                md.collect_to_result_frame(name, column, cd.cat_frame['result'], cd.cat_frame['mark'], bc_with_sum)
#                cd.cat_frame = md.date.join(cd.cat_frame)
#                cd.cat_frame = cd.cat_frame.set_index('DATE')
#                cd.cat_frame.to_excel(f'output_files/{month}/{name}/{name}:{column}.xlsx', sheet_name=column.replace(':', '_'))
#                #break
#        print(name)
#        md.get_day_sum_if_sleep_in_time(name, ad.mods_frame[name + '_sleep_in_time'])
#        md.result_frame[name].set_index('DATE').to_excel(f'output_files/{month}/{name}/{name}_total.xlsx', sheet_name='total')
#        print(pd.Series(result_dict), pd.Series(result_dict).sum())
