import pandas as pd

from temp_db.mirror_db import Mirror


mirror = Mirror()
mirror.init_frame()
date_ser = pd.Series(mirror.status_series.index, index=range(len(mirror.status_series)))
status_ser = mirror.status_series.copy()
status_ser.index = range(len(mirror.status_series))
df = pd.concat([date_ser, status_ser], axis=1, ignore_index=True)
print(df)
