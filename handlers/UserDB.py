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

    @property
    def row_in_process(self) -> int:
        return self.filler.row_in_process_index

    def is_date_busy(self, rows_in_process: list) -> bool:
        flag = False
        if self.filler.date_need_common_filling:
            if self.row_in_process in rows_in_process:
                flag = True
        return flag

    def get_inlines(self) -> list:
        self.inlines.extend(self.filler.cell_names_list)

    def set_last_message(self, message: Message):
        self.last_message = message


class UserDataBase:
    def __init__(self):
        self.db: dict = {}
        self.active_recipient: str = ''

    @property
    def r(self) -> str:
        return self.active_recipient

    @r.setter
    def r(self, recipient):
        self.active_recipient = recipient

    @property
    def r_data(self) -> FillingUser:
        return self.db[self.r]

    @property
    def rows_in_process(self) -> list:
        list_of_rows = []
        for r in self.db:
            row = self.db[r].filler.row_in_process_index
            if row is not None:
                list_of_rows.append(row)
        return list_of_rows

    def add_new_recipient(self, message: Message):
        self.r = message.from_user.first_name
        self.db[self.r] = FillingUser(self.r, message)

    def remove_recipient(self, message: Message):
        del self.db[message.from_user.first_name]
