import pandas as pd

class CombinationOfMods:
    def __init__(self, path_to_test, path_to_price=''):
        df = pd.read_csv(path_to_test, delimiter=';')
        limit = len([i for i in df['ANSWER'].fillna(0) if i > 0])
        df = df[0:limit]
        head = [i for i in df.columns.to_list() if 'Unnamed' not in i]
        variants = df[head]
        variants_dict = {}
        for key in variants:
            print(key)
            variants[key] = [i for i in variants[key].fillna(0)]

        # variants = {i: df[i] for i in head}







        print(variants)




        # self.c = test['ANSWER'].unique()
        # self.mod = [i for i in test['MOD'].to_list() if i]

        # print(test['MOD'].fillna(0)) # замена НаН на false
        # variants = {i: list(test[i]) for i in head}
        # for i in variants:
        #     print(type(i))
        #     for e in i:
        #         print(type(e))

        # self.weak = 0







                # answer_list.append(s)
        # for dict in answer_list:
        #     k


test = CombinationOfMods('months/dec22test/FOR_TEST.csv')