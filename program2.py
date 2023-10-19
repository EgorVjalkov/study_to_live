import classes as cl
import pandas as pd
from testing import does_need_correction
from analytic_utilities import FrameForAnalyse

recipients = ['Egr']
month = "oct23"

path_to_file = f'months/{month}/{month}.xlsx'
show_calc = True


def main():
    if not does_need_correction(pd.read_excel(path_to_file, sheet_name='price')):

        md = cl.MonthData(path_to_file)
        md.get_vedomost()
        md.get_price_frame()
        md.get_frames_for_working(limiting='for count')
        md.fill_na()
        for r_name in recipients:
            r = cl.Recipient(r_name, md.date)
            r.create_output_dir(f'output_files', month)
            r.get_and_collect_r_name_col(md.accessory['COM'], 'children')
            r.get_and_collect_r_name_col(md.accessory['PLACE'], 'place')
            r.get_and_collect_r_name_col(md.accessory['DUTY'], 'duty')
            r.get_family_col()
            r.get_duty_coefficients_col()
            r.get_children_coef_cols(md.accessory['KG'], md.accessory['WEAK'])
            r.get_place_coefficients_col()
            r.get_sleepless_coef_col(md.mother_frame)
            r.get_r_positions_col()
            r.get_all_coefs_col()
            r.mod_data.to_excel(f'output_files/{month}/{r_name}/{r_name}_mods.xlsx')
            r.get_r_vedomost(recipients, md.categories)
            print(r.cat_data)
            # fltr = FrameForAnalyse(df=r.cat_data)
            # fltr.filtration([('part', 'a:sleeptime', 'pos')])
            # for column in fltr.items:
            for column in r.cat_data:
                cd = cl.CategoryData(r.cat_data[column], r.mod_data, md.prices)
                print(cd.name)
                cd.add_price_column(show_calculation=show_calc)
                #print(cd.cat_frame)
                cd.add_coef_and_result_column(show_calculation=show_calc)
                bonus_column = cl.BonusFrame(cd.cat_frame, cd.price_frame)
                if bonus_column.has_bonus_logic():
                    cd.cat_frame['bonus'] = bonus_column.count_a_bonus()
                    bc_with_statistic = bonus_column.get_bonus_list_with_statistic()
                else:
                    bc_with_statistic = ()
                r.collect_to_result_frame(cd.get_result_col_with_statistic(), bc_with_statistic)
                cd.get_ready_and_save_to_excel(md.date, f'output_files/{month}/{r_name}/{cd.name}.xlsx')
            r.get_day_sum_if_sleep_in_time_and_save(f'output_files/{month}/{r_name}/{r_name}_total.xlsx')


if __name__ == '__main__':
    main()
