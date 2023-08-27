import pandas as pd
import program2 as prog2
from analytic_utilities import FrameForAnalyse

recp = ['Egr']
refresh_flag = False
#recp = prog2.recipients
# еще ечть идейка фильтрованный фрейм перезапустить
# придумай как сделать экстракт если фильтр идет не по колоннам а по индексу, скажем по статке, и здесь мешает дата и задник

for r_name in recp:
    path_to_output = f'output_files/{prog2.month}/{r_name}'
    path_to_total = path_to_output + f'/{r_name}_total.xlsx'
    mods_frame = pd.read_excel(path_to_output+f'/{r_name}_mods.xlsx').fillna('')

    if refresh_flag:
        prog2.main()

    frame_filtered = FrameForAnalyse(path_to_total)
    frame_filtered.filtration([('part', 'bonus', 'neg'), ('part', ':', 'pos')])
    categories = frame_filtered.present_by_items(frame_filtered.df, remove_stat=False)

    frame_filtered.items = frame_filtered.df['day_sum'].to_list()
    days_above_mean = frame_filtered.filtration([('>', 'mean', 'pos')], behavior='index_values')
    print(frame_filtered.items)

    frame_filtered.items = categories.tail(1).to_dict('records')[0]
    frame_filtered.filtration([('>', 'mean', 'pos')], behavior='rows_values')
    cats_above_mean = frame_filtered.present_by_items(categories)
    print(cats_above_mean)

    cats_above_mean = frame_filtered.present_by_items(cats_above_mean, by_previos_conditions=days_above_mean)
    print(cats_above_mean)


    # frame_filtered.df = frame_filtered.row_statistic

    # above_mean_total = frame_filtered.filtration({'>': 'mean'}, by_column='day_sum')
    # above_mean_items = frame_filtered.items

    # for cf in categories:
    #     cat_frame = pd.read_excel(path_to_output+f'/{cf}.xlsx')

    #     cf = frame_filtered.presentation_by_keys(cat_frame)
    #     print(cf)

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
