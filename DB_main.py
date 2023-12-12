import pandas as pd
from row_db.mirror_db import Mirror
from path_maker import PathMaker

#  серьезная замуть здесь с датами и переходом на другой месяц
# date = datetime.date.today()
# date = datetime.date(day=30, month=11, year=2023)

#path_to_temp_db = PathBy().to_temp_db
#day_db = UnfilledRowsDB()
path_to = PathMaker()
mirror = Mirror(path_to)
if mirror.no_dbs:
    mirror.init_temp_dbs()

if __name__ == '__main__':
    if mirror.need_scan:
        mirror.update_after_scan()
        mirror.update_by_date()
    else:
        mirror.update_by_date()
    print(mirror.series)
