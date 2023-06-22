import classes as cl
import os
import pandas as pd
from testing import does_need_correction


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

    md = cl.MonthData(path_to_file, recipients)
    for r_name in recipients:
        r = cl.Recipient(r_name, md.date)
        r.get_and_collect_r_name_col(md.accessory['COM'], 'children')
        r.get_and_collect_r_name_col(md.accessory['HOME'], 'home')
        r.get_and_collect_r_name_col(md.accessory['DUTY'], 'duty')
        r.get_children_coef_col(md.accessory['KG'])
        r.get_duty_coefficients_col()
        r.get_weak_coefficients_col(md.accessory['WEAK'])
        r.get_sleepless_col(md.vedomost)
        r.get_r_positions_col()
        r.get_all_coefs_col()
        print(r.mod_data)
