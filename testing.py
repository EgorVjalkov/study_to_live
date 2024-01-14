from colorama import Fore


def does_need_correction(price_frame):
    need_correction = False
    for cat in price_frame:
        filter_ = price_frame[cat].map(
            lambda i_: isinstance(i_, str) and '{' in i_)
        dict_cells = price_frame[cat][filter_ == True]
        wrong_dict = {}
        for i in dict_cells:
            try:
                check = eval(i)
            except SyntaxError:
                need_correction = True
                print(Fore.RED + f'{cat}, {i}' + Fore.RESET)
            else:
                print(f'{cat} is correct')
    return need_correction


# recipients = ['Egr', 'Lera']
# month = "m23"
# path_to_file = f'months/{month}/{month}.xlsx'
# show_calc = True
#
# prices = pd.read_excel(path_to_file, sheet_name='price')
# check_dicts_in_price_frame(prices)
