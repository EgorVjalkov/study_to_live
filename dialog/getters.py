from aiogram_dialog import DialogManager
from typing import Union

from DB_main import mirror

from dialog.start_handlers import bot, ADMIN_ID
from dialog.selected import get_filler

from filler.vedomost_filler import BaseFiller, VedomostCounter, CoefsFiller, ResultEmptyError
from filler.day_row import DayRow


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


def get_counter_report(counter: VedomostCounter) -> list:
    result_frame = counter.count_day_sum()
    day_sum = f'{round(result_frame["result"].sum(), 1)} p.'
    result_frame['result'] = result_frame['result'].map(lambda i: f'{str(i)} р.')
    result_dict = result_frame.T.to_dict('list')
    result_dict = {c: ' -> '.join(result_dict[c]) for c in result_dict}
    result_dict['сумма дня'] = day_sum
    rows_for_report = [f'За {counter.day.date_n_day_str} насчитано:']
    rows_for_report.extend([f'{c}: {result_dict[c]}' for c in result_dict])
    return rows_for_report


def get_answer_for_filling(date_n_day: str,
                           dict_for_rep: dict,
                           day_status: str = '',
                           mir_status: str = ''
                           ) -> list:
    answer_list = [
        f'За {date_n_day} заполнено:',
        f'статус дня: {day_status}',
        f'статус зеркала {mir_status}',
        ''
    ]
    answer_list.extend([f'{c} -> {dict_for_rep[c]}' for c in dict_for_rep])
    return answer_list


async def get_dates(dialog_manager: DialogManager,
                    **middleware_data) -> dict:

    filler: BaseFiller = get_filler(dialog_manager)
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

    filler: BaseFiller = get_filler(dialog_manager)
    data = {'categories': filler.categories_btns, 'can_save': filler.something_done}
    print(data)
    return data


async def get_vars(dialog_manager: DialogManager,
                   **middleware_data) -> dict:

    filler: BaseFiller = get_filler(dialog_manager)

    variants = [[i] for i in filler.active_cell_data.get_keys(filler.behavior, filler.day.name)]
    print(variants)
    data = {'variants': variants, 'topic': filler.active_cell_data.description}
    return data


async def get_topic(dialog_manager: DialogManager,
                    **middleware_data) -> dict:

    filler: BaseFiller = get_filler(dialog_manager)
    cat_name = filler.active_cell_name
    if filler.active_cell_data.has_some_value:
        old_value_sent = f'Предыдущее значение - {filler.active_cell_data.current_value}'
    else:
        old_value_sent = ''
    return {'cat_name': cat_name, 'old_value': old_value_sent}


async def get_report(dialog_manager: DialogManager,
                     **middleware_data) -> dict:

    program: Union[BaseFiller, CoefsFiller, VedomostCounter] = get_filler(dialog_manager)
    match program:
        case VedomostCounter():
            report = get_counter_report(program)

        case filler:
            dict_for_rep = filler.update_bd_and_get_dict_for_rep()
            report = get_answer_for_filling(filler.day.date_n_day_str,
                                            dict_for_rep,
                                            filler.day.STATUS,
                                            filler.mirror_status)
            counter = VedomostCounter(filler.recipient,
                                      DayRow(filler.day.day_row_for_saving))
            report.append('')
            #сделай здесь звездочки, тыж моежшь!
            report.extend(get_counter_report(counter))

    report = '\n'.join(report)

    user = dialog_manager.event.from_user
    if user.id != ADMIN_ID:
        await bot.send_message(ADMIN_ID, f'{user.first_name} завершил заполнение. {report}')

    return {'report': report}
