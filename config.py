import pathlib
from pathlib import Path


path_to_project = pathlib.Path.cwd()

month = 'dec23'
path_to_vedomost = Path(path_to_project, 'months', month, f'{month}.xlsx')
