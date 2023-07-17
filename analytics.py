import pandas as pd
from program2 import recipients, month


for r_name in recipients:
    path_to_output = f'output_files/{month}/{r_name}'
    path_to_total = path_to_output + f'/{r_name}_total.xlsx'
    result_frame = pd.read_excel(path_to_total)
    print(result_frame.index())
