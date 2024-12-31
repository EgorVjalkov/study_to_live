from datetime import datetime

from database.mirror import Mirror


mirror = Mirror()
#проба в тестовую дату
#mirror.date = datetime(day=1, month=1, year=2025).date()
mirror.init_series()

