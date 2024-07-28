from aiogram_dialog import DialogManager

from DB_main import mirror

from dialog.start_handlers import bot, ADMIN_ID
from dialog.selected import get_filler
from dialog.states import FillingVedomost, FillingSleeptime

from filler.vedomost_filler import VedomostFiller
from filler.vedomost_cell import VedomostCell


topics = {
    'filling': {
        'greet': 'Выберите дату для заполнения ведомости',
        'none': 'Все заполнено!'
    },
    'correction': {
        'greet': 'Выберите дату для коректировки',
        'none': 'Нечего исправлять'
    },
    'coefs': {
        'greet': 'Выберите дату для корректировки'}
    }


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
            answer_list.append(f'не могу рассчитать, какая-то ошибка {error}')
    return '\n'.join(answer_list)


async def get_dates(dialog_manager: DialogManager,
                    **middleware_data) -> dict:

    filler: VedomostFiller = get_filler(dialog_manager)
    topic_vars = topics.get(filler.behavior)

    if filler.need_work:
        topic = topic_vars.get('greet')
        cancel = 'завершить сеанс'
    else:
        topic = topic_vars.get('none')
        cancel = 'понятно'

    return {'dates': filler.days, 'topic': f"Привет! {topic}", 'cancel': cancel}


async def get_cats(dialog_manager: DialogManager,
                   **middleware_data) -> dict:

    filler: VedomostFiller = get_filler(dialog_manager)
    data = {'categories': filler.get_bnts_of_categories(), 'can_save': filler.something_done}
    print(data)
    return data


async def get_vars(dialog_manager: DialogManager,
                   **middleware_data) -> dict:

    filler: VedomostFiller = get_filler(dialog_manager)

    variants = [[i] for i in filler.active_cell_data.keys]
    if filler.behavior != 'coefs':
        variants.extend([['не мог'], ['забыл']])

    data = {'variants': variants, 'topic': filler.active_cell_data.description}
    return data


async def get_report(dialog_manager: DialogManager,
                     **middleware_data) -> dict:

    filler: VedomostFiller = get_filler(dialog_manager)
    updated = filler.update_day_row()
    mirror.update_db(updated)
    report = get_answer_if_finish(filler)

    user = dialog_manager.event.from_user
    if user.id != ADMIN_ID:
        await bot.send_message(ADMIN_ID, f'{user.username} завершил заполнение. {report}')

    return {'report': report}
