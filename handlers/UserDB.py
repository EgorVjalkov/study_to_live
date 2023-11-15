from aiogram.types import Message
from vedomost_filler import VedomostFiller
from config import path_to_vedomost


class FillingUser:
    def __init__(self, recipient: str, message: Message):
        username_dict = {'Jegor': 'Egr', 'Валерия': 'Lera'}
        self.r_name = recipient
        self.r_id = message.from_user.id
        self.filler = VedomostFiller(recipient=username_dict[self.r_name])
        self.filler.get_mother_frame_and_prices(path_to_vedomost)
        self.last_message = None
        self.inlines = []

    def get_inlines(self):
        self.inlines.extend(self.filler.cell_names_list)

    def set_last_message(self, message: Message):
        self.last_message = message


class UserDataBase:
    def __init__(self):
        self.db: dict = {}
        self.active_recipient: str = ''

    @property
    def r(self):
        return self.active_recipient

    @r.setter
    def r(self, recipient):
        self.active_recipient = recipient

    @property
    def r_data(self):
        return self.db[self.r]

    def add_new_recipient(self, message: Message):
        self.r = message.from_user.first_name
        self.db[self.r] = FillingUser(self.r, message)

    def remove_recipient(self, message: Message):
        del self.db[message.from_user.first_name]
