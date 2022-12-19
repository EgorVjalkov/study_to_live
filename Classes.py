import pandas as pd

class CombinationOfMods:
    def __init__(self, path_to_test, path_to_price=''):
        df = pd.read_csv(path_to_test, delimiter=';')
        test = df.iloc[0:6] # срезы
        # test[test['MOD']  True]
        print(test['MOD'].fillna(False)) # замена НаН на false
        # pd.DataFrame(test, index=None, columns=1)
        head = test.columns.to_list() # конвертация в list
        # head = [i for i in list(test.head(0)) if 'Unnamed' not in i]

        # self.c = test['ANSWER'].unique()
        print(head)
        self.mod = [i for i in test['MOD'].to_list() if i]

        print(self.mod)
        variants = {i: list(test[i]) for i in head}
        # for i in variants:
        #     print(type(i))
        #     for e in i:
        #         print(type(e))

        # self.weak = 0

        print(variants)






                # answer_list.append(s)
        # for dict in answer_list:
        #     k


test = CombinationOfMods('months/dec22test/FOR_TEST.csv')