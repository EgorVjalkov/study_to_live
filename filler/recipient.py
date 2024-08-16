from dataclasses import dataclass
from filler.day_row import DayRow


COMMON_POSITIONS = ['a', 'z', 'h', 'f']


@dataclass
class Recipient:
    name: str

    @property
    def litera(self):
        return self.name[0]

    @property
    def private_position(self):
        return self.litera.lower()

    @property
    def all_positions(self):
        return COMMON_POSITIONS.copy() + [self.private_position]


