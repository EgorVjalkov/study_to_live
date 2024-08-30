from aiogram_dialog import DialogManager

from DB_main import mirror

from dialog.start_handlers import bot, ADMIN_ID
from dialog.selected import get_filler
from dialog.states import FillingVedomost, FillingSleeptime

from filler.vedomost_filler import VedomostFiller, ResultEmptyError
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
        'greet': 'Выберите дату для корректировки'},
    'count': {
        'greet': 'Выбрите дату для расчета'},
    }


def get_counter_report(filler: VedomostFiller) -> list:
    result_frame = filler.count_day_sum()
    day_sum = f'{round(result_frame["result"].sum(), 1)} p.'
    result_frame['result'] = result_frame['result'].map(lambda i: f'{str(i)} р.')
    result_dict = result_frame.T.to_dict('list')
    result_dict = {c: ' -> '.join(result_dict[c]) for c in result_dict}
    result_dict['сумма дня'] = day_sum
    rows_for_report = [f'{c}: {result_dict[c]}' for c in result_dict]
    rows_for_report.insert(0, f'За {filler.day.date_n_day_str} насчитано:')
    return rows_for_report


def get_answer_if_finish(filler: VedomostFiller) -> str:
    filled: dict = filler.day.filled_recipient_cells_for_working
    answer_list = [f'За {filler.day.date_n_day_str} заполнено:']

    answer_list.extend([f'{c} -> {filled[c]}' for c in filled])
    try:
        answer_list.append('')
        answer_list.extend(get_counter_report(filler))
    except ResultEmptyError:
        return '\n'.join(answer_list)
    except BaseException as error:
        answer_list.append(f'не могу рассчитать, какая-то ошибка {error}')
    return '\n'.join(answer_list)


async def get_dates(dialog_manager: DialogManager,
                    **middleware_data) -> dict:

    filler: VedomostFiller = get_filler(dialog_manager)
    topic_vars = topics.get(filler.behavior)

    days = filler.day_btns
    if days:
        topic = topic_vars.get('greet')
        cancel = 'завершить сеанс'
    else:
        topic = topic_vars.get('none')
        cancel = 'понятно'

    return {'dates': days, 'topic': f"Привет! {topic}", 'cancel': cancel}


async def get_cats(dialog_manager: DialogManager,
                   **middleware_data) -> dict:

    filler: VedomostFiller = get_filler(dialog_manager)
    data = {'categories': filler.categories_btns, 'can_save': filler.something_done}
    print(data)
    return data


async def get_vars(dialog_manager: DialogManager,
                   **middleware_data) -> dict:

    filler: VedomostFiller = get_filler(dialog_manager)

    variants = [[i] for i in filler.active_cell_data.get_keys(filler.behavior, filler.day.name)]
    print(variants)
    data = {'variants': variants, 'topic': filler.active_cell_data.description}
    return data


async def get_topic(dialog_manager: DialogManager,
                    **middleware_data) -> dict:

    filler: VedomostFiller = get_filler(dialog_manager)
    cat_name = filler.active_cell_name
    if filler.active_cell_data.is_filled:
        old_value_sent = f'Предидущее значение - {filler.active_cell_data.current_value}'
    else:
        old_value_sent = ''
    return {'cat_name': cat_name, 'old_value': old_value_sent}


async def get_report(dialog_manager: DialogManager,
                     **middleware_data) -> dict:

    filler: VedomostFiller = get_filler(dialog_manager)
    if filler.behavior == 'count':
        return {'report': '\n'.join(
            get_counter_report(filler))}

    filler.update_day_row()
    report = get_answer_if_finish(filler)

    user = dialog_manager.event.from_user
    if user.id != ADMIN_ID:
        await bot.send_message(ADMIN_ID, f'{user.username} завершил заполнение. {report}')

    return {'report': report}
