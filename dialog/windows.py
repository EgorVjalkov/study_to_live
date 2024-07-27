from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Cancel, SwitchTo, Button

from dialog.states import FillingSleeptime, FillingVedomost
from dialog import getters, kbs, selected
from dialog.my_windows import CategoriesWindow


def greet_and_choose_date_menu() -> Window:
    return Window(
        Format('{topic}'),
        kbs.Keyboard('simple_by_item', 'date', 'dates'
                     ).get_kb(selected.on_chosen_date),
        Cancel(Format('{cancel}'),
               ),
        state=FillingVedomost.date_menu,
        getter=getters.get_dates,
    )


def categories_menu_if_simple() -> Window:
    return CategoriesWindow(
        kbs.Keyboard('simple_by_attr', 'cat', 'categories'
                     ).get_kb(selected.on_chosen_category),
        state=FillingVedomost.category_menu_if_simple,
    )


def categories_menu_if_scroll() -> Window:
    return CategoriesWindow(
        kbs.Keyboard('scroll_by_attr', 'cat', 'categories'
                     ).get_kb(selected.on_chosen_category),
        state=FillingVedomost.category_menu_if_scroll,
    )


def filling_menu() -> Window:
    return Window(
        Format('{topic}'),
        kbs.Keyboard('simple_by_item', 'vars', 'variants'
                     ).get_kb(selected.on_filling_category),
        Button(Const('<< назад'),
               id='sw_back',
               on_click=selected.on_back_to_category_menu),
        state=FillingVedomost.filling_menu,
        getter=getters.get_vars,
    )


def report_window() -> Window:
    return Window(
        Format("{report}"),
        Cancel(Const('понятно')),
        state=FillingVedomost.report_menu,
        getter=getters.get_report
    )


filler_dialog = Dialog(greet_and_choose_date_menu(),
                       categories_menu_if_simple(),
                       categories_menu_if_scroll(),
                       filling_menu(),
                       report_window()
                       )
