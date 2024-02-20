import datetime
import classes as cl
import pandas as pd

import path_maker
from testing import does_need_correction
from BonusColumn import BonusColumn
from temp_db.unfilled_rows_db import MonthDB
from filler.date_funcs import today


def main(recipients: list,
         data_frame: pd.DataFrame,
         price_frame: pd.DataFrame,
         filled_frame=True,
         month=False,
         demo_mode=False,
         show_calc=True,
         null_after_midnight=False) -> None | pd.DataFrame:

    assert not data_frame.empty
    md = cl.MonthData(mother_frame=data_frame, prices=price_frame)
    md.get_frames_for_working(filled_frame)
    md.fill_na()
    for r_name in recipients:
        r = cl.Recipient(r_name, md.date)
        r.get_mod_frame(md.accessory, md.categories)
        if not demo_mode:
            r.create_output_dir(f'output_files', month)
            r.mod_data.to_excel(f'output_files/{month}/{r_name}/{r_name}_mods.xlsx')
        r.get_r_vedomost(md.categories)
        # print(r.cat_data)
        for column in r.cat_data:
            cd = cl.CategoryData(r.cat_data[column], r.mod_data, md.prices, r.r_name)
            cd.add_price_column(show_calculation=show_calc)
            cd.add_mark_column(show_calculation=show_calc)
            cd.add_coef_and_result_column(show_calculation=show_calc)

            bc = BonusColumn(cd.cat_frame['mark'], cd.price_frame)
            if bc.bonus_logic and bc.enough_len:
                bc.count_a_bonus()
                # print(bc.mark_bonus_frame)
                cd.cat_frame[bc.name] = bc.get_bonus_ser_without_statistic()
                bc_with_statistic = bc.get_bonus_ser_with_statistic()
            else:
                bc_with_statistic = pd.Series(dtype='object')

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
                                                    demo_mode=demo_mode,
                                                    null_after_0=null_after_midnight)
        else:
            return r.result_frame


if __name__ == '__main__':
    #t = datetime.date(day=31, month=1, year=2024)
    t = today()
    path_to_mf = path_maker.path_to.mother_frame_by(t)
    price_fr = pd.read_excel(path_to_mf, sheet_name='price', index_col=0).fillna(0)
    if not does_need_correction(price_fr):
        main(['Egr', 'Lera'],
             MonthDB(path_to_mf=path_to_mf).mf_from_file,
             price_fr,
             month=path_maker.path_to.get_month(t),
             null_after_midnight=False)
