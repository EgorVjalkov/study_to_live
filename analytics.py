import pandas as pd
import program2 as prog2
from analytic_utilities import FrameForAnalyse

recp = ['Egr']
#recp = prog2.recipients

for r_name in recp:
    path_to_output = f'output_files/{prog2.month}/{r_name}'
    path_to_total = path_to_output + f'/{r_name}_total.xlsx'
    mods_frame = pd.read_excel(path_to_output+f'/{r_name}_mods.xlsx').fillna('')
    while True:
        try:
            frame_filtered = FrameForAnalyse(path_to_total)
            frame_filtered.extract_statistic()
            break
        except FileNotFoundError:
            prog2.main()

    frame_filtered.df = frame_filtered.date
    frame_filtered.filtration({'>': 5}, by_column='DAY')
    fltred = frame_filtered.presentation_by_keys(frame_filtered.father_object)
    mods = frame_filtered.presentation_by_keys(mods_frame)
    print(mods)
    cat_name_list = frame_filtered.items
    #frame_filtered.get_frame_by_flag(with_statistic_flag=False)
    #x = frame_filtered.filtration({'>': 'mean'}, by_row=2)
    #print(frame_filtered.object)
    #print(frame_filtered.df)
    #print('x', x)
    #print(frame_filtered.presentation_by_keys(frame_filtered.df))

   # for cf in cat_name_list:
   #     cf = FrameForAnalyse(path=path_to_output+f'/{cf}.xlsx')
   #     cf.df = frame_filtered.presentation_by_keys(cf.df)
   #     # print(cf.df)
   #     break

    #print(cat_name_list)
