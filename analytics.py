import pandas as pd
import program2 as prog2
from analytic_utilities import FrameForAnalyse

recp = ['Lera']
refresh_flag = False
#recp = prog2.recipients

for r_name in recp:
    path_to_output = f'output_files/{prog2.month}/{r_name}'
    path_to_total = path_to_output + f'/{r_name}_total.xlsx'
    mods_frame = pd.read_excel(path_to_output+f'/{r_name}_mods.xlsx').fillna('')

    if refresh_flag:
        prog2.main()

    frame_filtered = FrameForAnalyse(path_to_total)
    frame_filtered.extract_statistic()

    frame_filtered.df = frame_filtered.cat_statistic
    filtered_columns = frame_filtered.filtration({'>': 0}, by_row=32)
    total = frame_filtered.presentation_by_keys(frame_filtered.father_object)
    frame_filtered.df = mods_frame
    frame_filtered.df = frame_filtered.filtration({'=': 1}, by_column='dacha_coef')
    dacha_2child = frame_filtered.filtration({'=': 2}, by_column='child_coef')
    total_dacha = frame_filtered.presentation_by_keys(frame_filtered.father_object)
    frame_filtered.df = total_dacha
    frame_filtered.df = frame_filtered.filtration({'<': 'mean'}, by_column='day_sum')
    dacha_2child_index = frame_filtered.items

    day = frame_filtered.filtration({'positions': ['a']})
    print(day)

    for cf in day:
        cat_frame = pd.read_excel(path_to_output+f'/{cf}.xlsx')
        cf = frame_filtered.presentation_by_keys(cat_frame)
        print(cf)
   #     # print(cf.df)
   #     break

    #print(cat_name_list)
#sum_ = frame_filtered.presentation_by_keys(frame_filtered.df)
#print(sum_)

#frame_filtered.df = frame_filtered.date
#frame_filtered.filtration({'>': 5}, by_column='DAY')
#frame_filtered.get_frame_by_flag(with_statistic_flag=False)
#x = frame_filtered.filtration({'>': 'mean'}, by_row=2)
#print(frame_filtered.object)
#print(frame_filtered.df)
#print('x', x)
#print(frame_filtered.presentation_by_keys(frame_filtered.df))
