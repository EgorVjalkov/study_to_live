import pandas as pd
import program2 as prog2
import classes as cl
from analytic_utilities import FrameForAnalyse

recp = ['Egr']
refresh_flag = True
md = cl.MonthData(prog2.path_to_file)
#recp = prog2.recipients
# придумай как сделать экстракт если фильтр идет не по колоннам а по индексу, скажем по статке, и здесь мешает дата и задник
# калькулятор на время надо пересматривать, тестить, кажет херь

for r_name in recp:
    path_to_output = f'output_files/{prog2.month}/{r_name}'
    path_to_total = path_to_output + f'/{r_name}_total.xlsx'
    mods_frame = pd.read_excel(path_to_output+f'/{r_name}_mods.xlsx').fillna('')

    if refresh_flag:
        prog2.main()

    frame_filtered = FrameForAnalyse(path_to_total)
    frame_filtered.filtration([('part', 'bonus', 'neg'), ('part', ':', 'pos')])
    categories = frame_filtered.present_by_items(frame_filtered.df, remove_stat=False)

    frame_filtered.filtration([('part', 'bonus', 'pos')])
    bonus_frame = frame_filtered.present_by_items(frame_filtered.df)

    frame_filtered.items = frame_filtered.df['cat_day_sum'].to_list()
    days_above_mean = frame_filtered.filtration([('>', 'mean', 'pos')], behavior='index_values')

    frame_filtered.items = categories.tail(1).to_dict('records')[0]
    frame_filtered.filtration([('>', 'mean', 'pos')], behavior='rows_values')
    cats_above_mean = frame_filtered.present_by_items(categories)

    for i in cats_above_mean.columns:
        cat_frame = pd.read_excel(path_to_output+f'/{i}.xlsx')
        frame_filtered.items = list(cat_frame.columns)
        frame_filtered.filtration([('columns', ['DATE', 'DAY', 'mark'], 'neg')])
        cat_frame = frame_filtered.present_by_items(cat_frame)
        cat_frame_with_acc = pd.concat([md.date, md.accessory, cat_frame, frame_filtered.df['cat_day_sum']], axis=1)
        cat_frame_with_acc = frame_filtered.present_by_items(cat_frame_with_acc, by_previos_conditions=days_above_mean)
        #print(cat_frame_with_acc)
        cat_frame_with_acc.to_excel(f'{path_to_output}/___test_{i}.xlsx')


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
