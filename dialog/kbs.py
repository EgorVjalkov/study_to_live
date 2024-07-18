import operator

from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Group
from aiogram_dialog.widgets.text import Format

SCROLLING_HEIGHT = 5


def group_kb_by_item(on_click, id_: str, select_items: str):
    group_id = f'g_{id_}'
    select_id = f's_{id_}'
    return Group(
        Select(
            Format('{item[0]}'),
            id=select_id,
            item_id_getter=operator.itemgetter(0),
            items=select_items,
            on_click=on_click
        ),
        id=group_id,
        width=4
    )

def scrolling__kb_by_item(on_click, id_: str, select_items: str):
    group_id = f'g_{id_}'
    select_id = f's_{id_}'
    return ScrollingGroup(
        Select(
            Format('{item[0]}'),
            id=select_id,
            item_id_getter=operator.itemgetter(0),
            items=select_items,
            on_click=on_click
        ),
        id=group_id,
        width=1,
        height=SCROLLING_HEIGHT
    )


def group_kb_by_attr(on_click, id_: str, select_items: str, ):
    group_id = f'g_{id_}'
    select_id = f's_{id_}'
    return Group(
        Select(
            Format('{item.text}'), #
            id=select_id,
            item_id_getter=operator.attrgetter('id'),
            items=select_items,
            on_click=on_click
        ),
        id=group_id,
        width=1,
    )


def scroll_group_kb_by_attr(on_click, id_: str, select_items: str, ):
    group_id = f'g_{id_}'
    select_id = f's_{id_}'
    return ScrollingGroup(
        Select(
            Format('{item.text}'), #
            id=select_id,
            item_id_getter=operator.attrgetter('id'),
            items=select_items,
            on_click=on_click
        ),
        id=group_id,
        width=1,
        height=SCROLLING_HEIGHT
    )

