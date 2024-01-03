import datetime
from aiogram.types import Message, CallbackQuery
from filler.vedomost_filler import VedomostFiller
from utils.converter import Converter


username_dict = {'Jegor': 'Egr', 'Валерия': 'Lera'}
# жно переделать под ID


class Session:
    def __init__(self, message: Message, behavior: str):
        self.admin = username_dict[message.from_user.first_name]
        self.admin_id = message.from_user.id
        self.filler = VedomostFiller(self.admin, behavior).__call__()
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

    def manually_fill_sleep_time(self, now: datetime.datetime):
        message_day = now
        message_time = message_day.time()
        if message_time.hour in range(6, 21):
            category = self.filler.r_siesta
            new_value = '+'
        else:
            if message_time.hour in range(0, 6):
                message_time = datetime.time(hour=0, minute=0)
                message_day -= datetime.timedelta(days=1)

            category = self.filler.r_sleeptime
            new_value = datetime.time.strftime(message_time, '%H:%M')

        message_day = datetime.date.strftime(message_day, '%d.%m.%y')
        self.filler.change_a_day(message_day)
        self.filler.get_cells_ser(by_=category)
        self.filler.fill_the_cell(new_value)
        return self.filler


class SessionDB:
    def __init__(self):
        self.db: dict = {}
        self.recipient = None
        self.busy_dates = []

    def __repr__(self):
        return f'SessionDB({self.db.keys()})'

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

    def is_date_busy(self, date_from_tg):
        if isinstance(date_from_tg, str):
            date_from_tg = Converter(date_in_str=date_from_tg).to('date_object')
        return date_from_tg in self.dates_in_process

    def add_new_session_and_change_it(self, message: Message, behavior) -> Session:
        self.r = message.from_user.first_name
        self.db[self.r] = Session(message, behavior)
        return self.session

    def change_session(self, by_message: Message = None, by_name: str = None) -> Session:
        if by_message:
            self.r = by_message.from_user.first_name
        elif by_name:
            self.r = by_name
        return self.session

    def refresh_session(self, session: Session):
        self.session = session
        return self

    @property
    def dates_in_process(self) -> list:
        dates = [self.db[r_name].changed_date for r_name in self.db]
        return dates

    def remove_recipient(self, message: Message):
        del self.db[message.from_user.first_name]
