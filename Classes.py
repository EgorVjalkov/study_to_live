import pandas as pd

class CombinationOfMods:
    def __init__(self, path_to_test, path_to_price=''):
        test = pd.read_csv(path_to_test, delimiter=';')
        # pd.DataFrame(test, index=None, columns=1)
        # est = list(pd.DataFrame.columns)

        print(test['MOD'])






                # answer_list.append(s)
        # for dict in answer_list:
        #     k


test = CombinationOfMods('months/dec22test/FOR_TEST.csv')