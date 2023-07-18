import pandas as pd
import program2 as prog2
from analytic_utilities import FrameForAnalyse


for r_name in prog2.recipients:
    path_to_output = f'output_files/{prog2.month}/{r_name}'
    path_to_total = path_to_output + f'/{r_name}_total.xlsx'
    while True:
        try:
            result_frame = FrameForAnalyse(path_to_total)
            break
        except FileNotFoundError:
            prog2.main()

    filtered = result_frame.filtration('part', 'bonus')
    print(filtered)
