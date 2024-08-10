from sqlalchemy import create_engine

from connection_config import user, password, host, db_name
from temp_db.mirror_db import Mirror
from path_maker import PathMaker


path_to = PathMaker()
mirror = Mirror(path_to)


engine = create_engine(
    f'postgresql+psycopg2://{user}:{password}@{host}:5432/{db_name}')

if mirror.no_dbs:
    mirror.init_(from_='mf')
else:
    mirror.init_(from_='mf, but replace rows from temp_db')
