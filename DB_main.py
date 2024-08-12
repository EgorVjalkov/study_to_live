from temp_db.mirror_db import Mirror


mirror = Mirror().get_mirror_frame()
print(mirror.mirror_df)
dates_s = mirror.get_dates_for('Egr', 'correction')
print(dates_s)

