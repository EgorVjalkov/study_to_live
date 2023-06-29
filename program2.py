import classes as cl
import os
import pandas as pd
from testing import does_need_correction


recipients = ['Egr']
month = "jun23NEW_VERSION"

path_to_file = f'months/{month}/{month}.xlsx'
show_calc = True

if not does_need_correction(pd.read_excel(path_to_file, sheet_name='price')):

    while True:
        try:
            os.mkdir(f'output_files/{month}')
        except FileExistsError:
            break

    md = cl.MonthData(path_to_file, recipients)
    for r_name in recipients:
        r = cl.Recipient(r_name, md.date)
        r.get_and_collect_r_name_col(md.accessory['COM'], 'children')
        r.get_and_collect_r_name_col(md.accessory['HOME'], 'home')
        r.get_and_collect_r_name_col(md.accessory['DUTY'], 'duty')
        r.get_duty_coefficients_col()
        r.get_children_coef_col(md.accessory['KG'])
        r.get_weak_coefficients_col(md.accessory['WEAK'])
        r.get_sleepless_col(md.vedomost)
        print(r.mod_data)
        r.get_r_positions_col()
        r.get_all_coefs_col()
        #for_self_control = r.mod_data.get(['positions', 'coefs'])
        #for_self_control.to_excel(f'output_files/{month}/{r_name}_self_control_NEW.xlsx')
        r.get_r_vedomost(recipients, md.categories)
        for column in r.cat_data:
            if column.islower():
                column = 'e:silence'
                cd = cl.CategoryData(r.cat_data[column], r.mod_data, md.prices)
                cd.add_price_column(show_calculation=show_calc)
                cd.add_coef_and_result_column(show_calculation=show_calc)
                bonus_column = cl.BonusFrame(cd.cat_frame, cd.price_frame)
                if bonus_column.has_bonus_logic():
                    cd.cat_frame['bonus'] = bonus_column.count_a_bonus()
                    # result_dict[column+'_bonus'] = cd.cat_frame['bonus'].sum()
                    bc_with_sum = bonus_column.get_bonus_list_with_sum()
                else:
                    bc_with_sum = ()
                cd.cat_frame.to_excel(f'output_files/{cd.name}_testing.xlsx')
                md.collect_to_result_frame(r.r_name, column, cd.cat_frame['result'], cd.cat_frame['mark'], bc_with_sum)
                break
        md.result_frame[r_name].set_index('DATE').to_excel(f'output_files/{month}/{r_name}/{r_name}_total.xlsx')
        #break

