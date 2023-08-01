import pandas as pd
import program2 as prog2
from analytic_utilities import FrameForAnalyse

recp = ['Egr']
#recp = prog2.recipients

for r_name in recp:
    path_to_output = f'output_files/{prog2.month}/{r_name}'
    path_to_total = path_to_output + f'/{r_name}_total.xlsx'
    result_frame = pd.read_excel(path_to_total)
    # замуть так же с получением среднего, нужно настроить, чтоб не брал в расчет всякие строчки
    # здесь замуть с лишними категориями!!!!, надо сразу же в конструкторе их кусковать, определяя в зависимости от роу или солумн, что отрезать
    stat_of_categories = result_frame[-2:]
    stat_of_days = result_frame.get(['day_sum', ])
    while True:
        try:
            frame_filtered = FrameForAnalyse(path_to_total)
            frame_filtered.extract_statistic()
            break
        except FileNotFoundError:
            prog2.main()

    frame_filtered.df = frame_filtered.filtration({'part': ':', 'positions': ['a']})
    cat_name_list = frame_filtered.items
    #frame_filtered.get_frame_by_flag(with_statistic_flag=False)
    x = frame_filtered.filtration({'>': 'mean'}, by_row=2)
    print(frame_filtered.object)
    print(frame_filtered.df)
    print('x', x)
    print(frame_filtered.presentation_by_keys(frame_filtered.df))

    for cf in cat_name_list:
        cf = FrameForAnalyse(path=path_to_output+f'/{cf}.xlsx')
        cf.df = frame_filtered.presentation_by_keys(cf.df)
        # print(cf.df)
        break

    #print(cat_name_list)
