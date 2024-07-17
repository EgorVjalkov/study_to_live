from typing import Optional

from aiogram_dialog import DialogManager
from aiogram.fsm.state import State

from dialog.selected import get_filler, set_filler
from filler.vedomost_filler import VedomostFiller
from DB_main import mirror
from dialog.start_handlers import bot, ADMIN_ID


def get_answer_if_r_data_is_filled(filler: VedomostFiller) -> list:
    result_frame = filler.count_day_sum()
    result_frame['result'] = result_frame['result'].map(lambda i: 0 if isinstance(i, str) else i)
    day_sum = f'{str(result_frame["result"].sum())} p.'
    result_frame['result'] = result_frame['result'].map(lambda i: f'{str(i)} р.')
    print(result_frame["result"])
    result_dict = result_frame.T.to_dict('list')
    result_dict = {c: ' -> '.join(result_dict[c]) for c in result_dict}
    result_dict['сумма дня'] = day_sum
    return filler.filled_cells_list_for_print(result_dict)


def get_answer_if_finish(filler: VedomostFiller) -> str:
    answer_list = [f'За {filler.date_to_str} заполнено:']

    if filler.behavior == 'coefs':
        answer_list.extend(filler.acc_in_str)
    else:
        answer_list.extend(filler.filled_cells_list_for_print())
    print(filler.is_r_categories_filled)
    if filler.is_r_categories_filled:
        answer_list.append('')
        try:
            answer_list.append(f'За {filler.date_to_str} насчитано:')
            answer_list.extend(get_answer_if_r_data_is_filled(filler))
        except BaseException as error:
            print(f'ошибка: {error}')
            answer_list.append('не могу рассчитать, какая-то ошибка')
    return '\n'.join(answer_list)


async def get_dates(dialog_manager: DialogManager,
                    **middleware_data) -> dict:

    ctx = dialog_manager.start_data
    print(ctx)
    filler: VedomostFiller = get_filler(dialog_manager)
    data = {'dates': filler.days}
    return data


async def get_report(dialog_manager: DialogManager,
                     **middleware_data) -> dict:

    filler: VedomostFiller = get_filler(dialog_manager)
    if filler.already_filled_dict:
        filler.collect_data_to_day_row()
        mirror.save_day_data(filler.day)
        print(filler.already_filled_dict)
        report = get_answer_if_finish(filler)
    else:
        report = 'Вы ничего не заполнили'

    user = dialog_manager.event.from_user
    if not user.id != ADMIN_ID:
        await bot.send_message(ADMIN_ID, f'{user.username} завершил заполнение. {report}')

    print(dialog_manager.start_data)
    return {'report': report}

