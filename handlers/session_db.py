import asyncio
import datetime
from typing import Callable

from aiogram.types import Message
from filler.vedomost_filler import VedomostFiller
from utils.converter import Converter


username_dict = {'Jegor': 'Egr', 'Валерия': 'Lera'}
# жно переделать под ID


class Session:
    def __init__(self, message: Message, behavior: str):
        self.user = message.from_user.first_name
        self.user_id = message.from_user.id
        self.recipient = username_dict[self.user]
        self.filler = VedomostFiller(self.recipient, behavior).__call__()
        self.last_message = None
        self.inlines = []

    @property
    def changed_date(self) -> datetime.date:
        if self.filler.day:
            return self.filler.day.date

    def get_inlines(self):
        self.inlines.extend(self.filler.unfilled_cells)

    def set_last_message(self, message: Message):
        self.last_message = message

    def manually_fill_sleep_time(self, now: datetime.datetime) -> VedomostFiller:
        message_day = now
        message_time = message_day.time()
        print(message_time, 'inside func')
        if message_time.hour in range(6, 21):
            category = self.filler.r_siesta
            new_value = '+'
        else:
            if message_time.hour in range(0, 6):
                message_time = datetime.time(hour=0, minute=0)
                message_day -= datetime.timedelta(days=1)

            category = self.filler.r_sleeptime
            new_value = datetime.time.strftime(message_time, '%H:%M')

        self.filler.change_a_day(message_day.date())
        self.filler.get_cells_ser(by_=category)
        self.filler.fill_the_cell(new_value)
        return self.filler

    def get_answer_if_r_data_is_filled(self) -> list:
        result_frame = self.filler.count_day_sum()
        result_frame['result'] = result_frame['result'].map(lambda i: 0 if isinstance(i, str) else i)
        day_sum = f'{str(result_frame["result"].sum())} p.'
        result_frame['result'] = result_frame['result'].map(lambda i: f'{str(i)} р.')
        print(result_frame["result"])
        result_dict = result_frame.T.to_dict('list')
        result_dict = {c: ' -> '.join(result_dict[c]) for c in result_dict}
        result_dict['сумма дня'] = day_sum
        return self.filler.filled_cells_list_for_print(result_dict)

    def get_answer_if_finish(self) -> str:
        answer_list = [f'За {self.filler.date_to_str} заполнено:']

        if self.filler.behavior == 'coefs':
            answer_list.extend(self.filler.acc_in_str)
        else:
            answer_list.extend(self.filler.filled_cells_list_for_print())
        print(self.filler.is_r_categories_filled)
        if self.filler.is_r_categories_filled:
            answer_list.append('')
            try:
                answer_list.append(f'За {self.filler.date_to_str} насчитано:')
                answer_list.extend(self.get_answer_if_r_data_is_filled())
            except BaseException as error:
                print(f'ошибка: {error}')
                answer_list.append('не могу рассчитать, какая-то ошибка')
        return '\n'.join(answer_list)


class SessionDB:
    def __init__(self):
        self.db: dict = {}
        self.recipient = None
        self.superuser_id = 831647128

    def __repr__(self):
        repr_dict = {r: self.db[r].changed_date for r in self.db}
        repr_dict = {r: Converter(date_object=repr_dict[r]).to('str')
                     for r in repr_dict}
        return f'SessionDB({repr_dict})'

    @property
    def r(self) -> str:
        return self.recipient

    @r.setter
    def r(self, r_name):
        self.recipient = r_name

    @property
    def session(self) -> Session:
        return self.db[self.r]

    @session.setter
    def session(self, session: Session):
        self.db[self.r] = session

    @property
    def dates_in_process(self):
        return [self.db[r].changed_date for r in self.db]

    def is_superuser(self, message: Message) -> bool:
        return message.from_user.id == self.superuser_id

    def is_date_busy(self, date_from_tg: str | datetime.date):
        if isinstance(date_from_tg, str):
            date_from_tg = Converter(date_in_str=date_from_tg).to('date_object')
        return date_from_tg in self.dates_in_process

    def add_new_session_and_checkout(self, message: Message, behavior) -> Session:
        self.r = message.from_user.first_name
        self.session = Session(message, behavior)
        return self.session

    def switch_session(self, by_message: Message = None, by_name: str = None) -> Session:
        if by_message:
            self.r = by_message.from_user.first_name
        elif by_name:
            self.r = by_name
        return self.session

    def refresh_session(self, session: Session):
        self.session = session
        return self

    def remove_recipient(self, message: Message):
        del self.db[message.from_user.first_name]

    async def date_dispatcher(self,
                              date: str | datetime.date,
                              func: Callable,
                              *args,
                              **kwargs):

        if not self.is_date_busy(date):
            await func(*args, **kwargs)
        else:
            await asyncio.sleep(2)
            await self.date_dispatcher(date, func, *args, **kwargs)
