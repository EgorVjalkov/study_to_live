from temp_db.mirror_db import Mirror
from path_maker import PathMaker


path_to = PathMaker()
mirror = Mirror(path_to)

if mirror.no_dbs:
    mirror.init_(from_='mf')
else:
    mirror.init_(from_='mf, but replace rows from temp_db')
