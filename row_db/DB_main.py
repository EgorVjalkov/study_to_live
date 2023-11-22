from row_db.row_db import DayRowsDB
from path_maker import PathToVedomost

path = PathToVedomost().to_temp_db
day_db = DayRowsDB(path)
