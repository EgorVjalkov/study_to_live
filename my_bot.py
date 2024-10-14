from typing import Optional
from aiogram import Bot
from config_reader import config

class MyBot:
    def __init__(self):
        self.modification: Optional[str] = None

    @property
    def mode(self):
        return self.modification

    @mode.setter
    def mode(self, mod: str):
        self.modification = mod

    def get_bot(self):
        return Bot(config.get_token(self.mode))

my_bot = MyBot()
