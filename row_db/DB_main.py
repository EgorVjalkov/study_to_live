import datetime

from row_db.row_db import UnfilledRowsDB
from path_maker import PathTo

#  серьезная замуть здесь с датами и переходом на другой месяц
# date = datetime.date.today()
date = datetime.date(day=30, month=11, year=2023)

path_to_temp_db = PathTo().temp_db
path_to_mother_frame = PathTo(date).vedomost
day_db = UnfilledRowsDB(path_to_temp_db, path_to_mother_frame)
