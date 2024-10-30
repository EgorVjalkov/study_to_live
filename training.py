from filler.vedomost_filler import BaseFiller
from DB_main import mirror

if __name__ == '__main__':

    filler = BaseFiller('Lera', 'filling')

    print(mirror.series)
    filler()
    dayz = filler.day_btns
    print(dayz)
    for i in dayz:
        filler.change_day(i[0])
        filler.filter_cells()
        print(filler.working_space)
        #if filler.working_space.empty:
        #    filler.day.STATUS = 'Y'
        #    row = filler.day.day_row_for_saving
        #    mirror.update_vedomost(row)
