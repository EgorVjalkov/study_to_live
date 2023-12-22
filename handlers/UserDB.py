import pandas as pd
from aiogram.types import Message
from vedomost_filler import VedomostFiller
# тся вопрос о запуске филлера. Филлер он скачет от даты


class Session:
    def __init__(self, message: Message, behavior: str):
        self.username_dict = {'Jegor': 'Egr', 'Валерия': 'Lera'}  # здеся нужно по ID
        self.admin = message.from_user.first_name
        self.admin_id = message.from_user.id
        self.filler = VedomostFiller(self.admin, behavior).__call__()
        self.last_message = None
        self.inlines = []

    @property
    def row_in_process(self) -> int:
        return self.filler.day.date

    def is_date_busy(self, rows_in_process: list) -> bool:
        flag = False
        if self.filler.date_need_common_filling:
            if self.row_in_process in rows_in_process:
                flag = True
        return flag

    def get_inlines(self):
        self.inlines.extend(self.filler.unfilled_cells)

    def set_last_message(self, message: Message):
        self.last_message = message


class SessionDB:
    def __init__(self):
        self.db: dict = {}
        self.changed_date = None

    @property
    def date(self) -> str:
        return self.changed_date

    @date.setter
    def date(self, new_date):
        self.changed_date = new_date

    @property
    def session(self) -> Session:
        return self.db[self.r]

    @property
    def dates_in_process(self) -> list:
        return list(self.db.keys())

   # def add_new_session(self, session: Message, behavior):
   #     self.date = message.from_user.
   #     self.db[self.r] = Session(message, behavior).__call__()

    def remove_recipient(self, message: Message):
        del self.db[message.from_user.first_name]


