from temp_db.mirror_db import Mirror
from path_maker import PathMaker

print('пуск')

path_to = PathMaker()
mirror = Mirror(path_to)

if mirror.no_dbs:
    mirror.init_temp_dbs()
else:
    mirror.update_by_dbs()
print(mirror.series)

#if __name__ == '__main__':
#    if mirror.need_scan:
#        mirror.update_after_()
#        mirror.update_by_date()
#    else:
#        mirror.update_by_date()
#    print(mirror.series)
