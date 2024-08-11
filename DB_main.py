from sqlalchemy import create_engine

from connection_config import user, password, host, db_name
from temp_db.mirror_db import Mirror


engine = create_engine(
    f'postgresql+psycopg2://{user}:{password}@{host}:5432/{db_name}')

mirror = Mirror(engine).update_mirror_from_mf()
print(mirror.mirror_df)
dates_s = mirror.get_dates_for('Egr', 'correction')
print(dates_s)

