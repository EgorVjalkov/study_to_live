import datetime
import pandas as pd

import counter.classes as cl
from testing import does_need_correction
from counter.BonusColumn import BonusColumn
from filler.date_funcs import last_date_of_past_month
from database.mirror import Mirror, get_month


not_count_categories = ['a:sleeptime', 'z:sleeptime']


def main(recipients: list,
         data_frame: pd.DataFrame,
         price_frame: pd.DataFrame,
         filled_frame=True,
         month: str = '',
         demo_mode: bool = False,
         show_calc: bool = True,
         null_after_midnight: bool = False) -> None | pd.DataFrame:

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

        r.get_r_vedomost(md.categories, not_count_categories)
        # print(r.cat_data)
        for column in r.cat_data:
            # column = 'e:velo'
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
                                           f'output_files/{month}/{r_name}/{cd.name.replace(":","_")}.xlsx',
                                           demo_mode=demo_mode)

            if not demo_mode:
                result_col = cd.get_result_col_with_statistic()
            else:
                result_col = cd.cat_frame['result']
                result_col.name = column
                print(result_col)
            r.collect_to_result_frame(result_col,
                                      bc_with_statistic)

        if not demo_mode:
            r.get_day_sum_if_sleep_in_time_and_save(f'output_files/{month}/{r_name}/{r_name}_total.xlsx',
                                                    demo_mode=demo_mode,
                                                    null_after_0=null_after_midnight)
        else:
            return r.result_frame


if __name__ == '__main__':
    mirror2 = Mirror()
    mirror2.date = last_date_of_past_month(datetime.date.today())
    mirror2.init_series()
    vedomost = mirror2.get_vedomost(mirror2.date)
    price = mirror2.get_cells_data('filling', date=mirror2.date)
    if not does_need_correction(price):
        main(['Egr', 'Lera'],
             vedomost,
             price,
             month=get_month(mirror2.date),
             null_after_midnight=False,
             )

