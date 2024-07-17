from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Cancel, SwitchTo
from aiogram_dialog.widgets.input.text import TextInput

from dialog.states import FillingSleeptime, FillingVedomost
from dialog import getters, kbs, selected


def greet_and_choose_date_menu() -> Window:
    return Window(
        Const('Выберите функцию для расчетов'),
        kbs.group_kb_by_item(selected.on_chosen_date,
                             'date', 'dates'),
        SwitchTo(Const('Завершить сеанс'),
                 id='sw_report',
                 state=FillingVedomost.report_menu),
        state=FillingVedomost.date_menu,
        getter=getters.get_dates,
    )


def report_window() -> Window:
    return Window(
        Format("{report}"),
        state=FillingVedomost.report_menu,
        getter=getters.get_report
    )


filler_dialog = Dialog(greet_and_choose_date_menu(),
                       report_window()
                       )
