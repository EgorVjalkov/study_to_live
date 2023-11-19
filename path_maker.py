import pathlib
from pathlib import Path
from os import mkdir


path_to_project = pathlib.Path.cwd()

month = 'nov23'
path_to_vedomost = Path(path_to_project, 'months', month, f'{month}.xlsx')

temp_dir = f'{month}_temp_db'
path_to_temp_db = Path(path_to_project, 'months', month, temp_dir)
if os.
print(path_to_temp_db)
