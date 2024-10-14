import datetime
from filler.date_funcs import yesterday, get_dates_list


def set_filter(today_for_filling: datetime.date,
               recipient: str,
               behavior: str,
               ) -> dict:

    done_mark = recipient[0]
    yesterday_ = yesterday(today_for_filling)

    recipes_dict = {
        'filling': {
            'STATUS': lambda i: i not in ['Y', done_mark],
            'DATE': lambda i: i <= today_for_filling,
        },
        'correction': {
            'STATUS': lambda i: i not in ['empty'],
            'DATE': lambda i: i in [yesterday_, today_for_filling],
        },
        'coefs': {
            'DATE': lambda i: i in get_dates_list(today_for_filling, -7, 7)
        },
        'count': {
            'STATUS': lambda i: i in ['Y', done_mark],
            'DATE': lambda i: i in get_dates_list(today_for_filling, -7, 0)
        }}

    return recipes_dict.get(behavior)
