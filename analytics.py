import pandas as pd
import program2 as prog2
from analytic_utilities import FrameForAnalyse

recp = ['Egr']
#recp = prog2.recipients

for r_name in recp:
    path_to_output = f'output_files/{prog2.month}/{r_name}'
    path_to_total = path_to_output + f'/{r_name}_total.xlsx'
    while True:
        try:
            frame_filtered = FrameForAnalyse(path_to_total)
            break
        except FileNotFoundError:
            prog2.main()

    frame_filtered.filtration({'part': ':', 'positions': ['a']})
    cat_name_list = frame_filtered.filtered_keys
    frame_filtered.get_frame_by_flag(with_statistic_flag=False)
    frame_filtered.filtration({'>': 'mean'}, by_column='a:titi')

    for cf in cat_name_list:
        cf = FrameForAnalyse(path=path_to_output+f'/{cf}.xlsx')
        cf.df = frame_filtered.presentation_by_keys(cf.df)
        print(cf.df)
        break

    #print(cat_name_list)
