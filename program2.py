import classes as cl
import os
import pandas as pd
from testing import does_need_correction
from statistic import InnerIterObject


recipients = ['Egr', 'Lera']
month = "jun23NEW_VERSION"

path_to_file = f'months/{month}/{month}.xlsx'
show_calc = True

if not does_need_correction(pd.read_excel(path_to_file, sheet_name='price')):

    while True:
        try:
            os.mkdir(f'output_files/{month}')
        except FileExistsError:
            break

    md = cl.MonthData(path_to_file)
    for r_name in recipients:
        r = cl.Recipient(r_name, md.date)
        r.get_and_collect_r_name_col(md.accessory['COM'], 'children')
        r.get_and_collect_r_name_col(md.accessory['PLACE'], 'place')
        r.get_and_collect_r_name_col(md.accessory['DUTY'], 'duty')
        r.get_duty_coefficients_col()
        r.get_children_coef_cols(md.accessory['KG'], md.accessory['WEAK'])
        r.get_place_coefficients_col()
        # for_self_control = r.mod_data.get([i for i in r.mod_data if 'coef' in i])
        # for_self_control.to_excel(f'output_files/{month}/{r_name}_self_control_NEW.xlsx')
        r.get_sleepless_coef_col(md.vedomost)
        r.get_r_positions_col()
        r.get_all_coefs_col()
        # print(r.mod_data)
        # for_self_control = r.mod_data.get(['positions', 'coefs'])
        # for_self_control.to_excel(f'output_files/{month}/{r_name}_self_control_NEW.xlsx')
        r.get_r_vedomost(recipients, md.categories)
        filtered_cat_frame = InnerIterObject(r.cat_data).filter(positions=[])
        #print(filtered_cat_frame)
        if not filtered_cat_frame.empty:
            for column in filtered_cat_frame:
                cd = cl.CategoryData(r.cat_data[column], r.mod_data, md.prices)
                cd.add_price_column(show_calculation=show_calc)
                cd.add_coef_and_result_column(show_calculation=show_calc)
                bonus_column = cl.BonusFrame(cd.cat_frame, cd.price_frame)
                if bonus_column.has_bonus_logic():
                    cd.cat_frame['bonus'] = bonus_column.count_a_bonus()
                    bc_with_statistic = bonus_column.get_bonus_list_with_statistic()
                else:
                    bc_with_statistic = ()
                r.collect_to_result_frame(cd.get_result_col_with_statistic(), bc_with_statistic)
                cd.get_ready_and_save_to_excel(md.date, f'output_files/{month}/{r_name}/{cd.name}.xlsx')
            filtered = InnerIterObject(r.result_frame).filter(filter_logic='negative', name_part='_bonus')
            r.get_result_frame_after_filter(filtered)
            r.get_day_sum_if_sleep_in_time_and_save(f'output_files/{month}/{r_name}/{r_name}_total.xlsx')
            df = r.create_frame(r.result_frame)
            print(df)
