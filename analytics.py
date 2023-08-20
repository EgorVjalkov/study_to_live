import pandas as pd
import program2 as prog2
from analytic_utilities import FrameForAnalyse

recp = ['Lera']
refresh_flag = True
#recp = prog2.recipients
# могет луче сразу по колонне фильтровать, а потом просто строить фрейм по индесу
# да, а фильтрация возращать будет айтемы, по которым и будем фильтровать любые фрейма
# с отрезком статистики: важно резать только лишь предметный объект, т.е. день или категорию

for r_name in recp:
    path_to_output = f'output_files/{prog2.month}/{r_name}'
    path_to_total = path_to_output + f'/{r_name}_total.xlsx'
    mods_frame = pd.read_excel(path_to_output+f'/{r_name}_mods.xlsx').fillna('')

    if refresh_flag:
        prog2.main()

    frame_filtered = FrameForAnalyse(path_to_total)
    frame_filtered.extract_statistic()
    categories = frame_filtered.filtration({'part': 'bonus'}, filter_logic='neg')

    frame_filtered.df = frame_filtered.row_statistic

    above_mean_total = frame_filtered.filtration({'>': 'mean'}, by_column='day_sum')
    above_mean_items = frame_filtered.items

    for cf in categories:
        cat_frame = pd.read_excel(path_to_output+f'/{cf}.xlsx')

        cf = frame_filtered.presentation_by_keys(cat_frame)
        print(cf)

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
