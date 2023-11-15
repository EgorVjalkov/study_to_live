import pathlib
from pathlib import Path


path_to_project = pathlib.Path.cwd()

month = 'nov23'
path_to_vedomost = Path(path_to_project, 'months', month, f'{month}.xlsx')
