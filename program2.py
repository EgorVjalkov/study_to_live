import classes as cl
import pandas as pd

import path_maker
from testing import does_need_correction
from BonusColumn import BonusColumn
from temp_db.unfilled_rows_db import MonthDB
from filler.date_funcs import today


def main(recipients, data_frame, price_frame, month=False, demo_mode=False, show_calc=True):
    md = cl.MonthData(mother_frame=data_frame, prices=price_frame)
    md.get_frames_for_working()
    md.fill_na()
    for r_name in recipients:
        r = cl.Recipient(r_name, md.date)
        r.get_mod_frame(md.accessory, md.categories)
        if not demo_mode:
            r.create_output_dir(f'output_files', month)
            r.mod_data.to_excel(f'output_files/{month}/{r_name}/{r_name}_mods.xlsx')
        r.get_r_vedomost(['Egr', 'Lera'], md.categories)
        # fltr = FrameForAnalyse(df=r.cat_data)
        # cat_filter = ('positions', ['a', 'z', 'h'], 'pos')
        # fltr.filtration([cat_filter])
        # for column in fltr.items:
        print(r.cat_data)
        for column in r.cat_data:
            cd = cl.CategoryData(r.cat_data[column], r.mod_data, md.prices, r.r_name)
            cd.add_price_column(show_calculation=show_calc)
            cd.add_mark_column(show_calculation=show_calc)
            cd.add_coef_and_result_column(show_calculation=show_calc)
            print(cd.cat_frame)

            bc = BonusColumn(cd.cat_frame['mark'], cd.price_frame)
            if bc.bonus_logic and bc.enough_len:
                bc.count_a_bonus()
                cd.cat_frame[bc.name] = bc.get_bonus_ser_without_statistic()
                bc_with_statistic = bc.get_bonus_ser_with_statistic()
            else:
                bc_with_statistic = pd.Series()

            cd.get_ready_and_save_to_excel(md.date,
                                           f'output_files/{month}/{r_name}/{cd.name}.xlsx',
                                           demo_mode=demo_mode)

            if not demo_mode:
                result_col = cd.get_result_col_with_statistic()
            else:
                result_col = cd.cat_frame['result']
                result_col.name = column
            r.collect_to_result_frame(result_col,
                                      bc_with_statistic)

        if not demo_mode:
            r.get_day_sum_if_sleep_in_time_and_save(f'output_files/{month}/{r_name}/{r_name}_total.xlsx',
                                                    demo_mode=demo_mode)
        else:
            return r.result_frame


if __name__ == '__main__':
    t = today()
    path_to_mf = path_maker.path_to.mother_frame_by(t)
    price_frame = pd.read_excel(path_to_mf, sheet_name='price', index_col=0).fillna(0)
    if not does_need_correction(price_frame):
        main(['Egr', 'Lera'],
             MonthDB(path_to_mf=path_to_mf).mf_from_file,
             price_frame,
             path_maker.path_to.get_month(t))
