from aiogram.fsm.state import State
from aiogram_dialog import Window
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import SwitchTo, Group, ScrollingGroup, Button

from dialog import kbs, selected, getters, states


class CategoriesWindow(Window):
    def __init__(self,
                 keyboard: Group | ScrollingGroup,
                 state: State):
        super().__init__(
            Const('Выберите категорию'),
            keyboard,
            SwitchTo(Const('<< назад'),
                     id='sw_back',
                     state=states.FillingVedomost.date_menu,
                     on_click=selected.on_back_to_date_menu),
            SwitchTo(Const('сохранить'),
                     id='sw_report',
                     state=states.FillingVedomost.report_menu,
                     when='can_save'),
            state=state,
            getter=getters.get_cats,
        )
