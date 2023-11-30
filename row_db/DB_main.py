from row_db.row_db import UnfilledRowsDB
from path_maker import PathTo

path_to_temp_db = PathTo().temp_db
path_to_mother_frame = PathTo().vedomost
day_db = UnfilledRowsDB(path_to_temp_db, path_to_mother_frame)
