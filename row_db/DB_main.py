import datetime

from row_db.row_db import UnfilledRowsDB
from path_maker import PathBy

#  серьезная замуть здесь с датами и переходом на другой месяц
date = datetime.date.today()
# date = datetime.date(day=30, month=11, year=2023)

path_to_temp_db = PathBy().to_temp_db
day_db = UnfilledRowsDB()
