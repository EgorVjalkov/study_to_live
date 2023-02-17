import pandas as pd
from random import choice, randint


class TestingPrices:
    def __init__(self, path_to_test, path_to_price=''):
        self.path_to_test = path_to_test
        self.path_to_price = path_to_price
        self.categories = {}
        self.test = []
        self.path_to_newtest = 'tests/new_test.csv'

    def read_and_filter(self):
        df = pd.read_csv(self.path_to_test, delimiter=';')
        limit = len([i for i in df['ANSWER'].fillna(0) if i > 0])
        df = df[0:limit]
        head = [i for i in df.columns.to_list() if 'Unnamed' not in i]
        variants = df[head]
        for key in variants:
            if key != 'ANSWER':
                variants[key] = [int(i) if type(i) == float else i for i in variants[key].fillna(0)]
                variants[key] = [str(i) if i else '' for i in variants[key]]
                self.categories[key] = variants[key].unique().tolist()
        return self.categories

    def create_a_testframe(self, days=1, category_key='', to_file=True):

        def testtime(time_list):
            time = choice(time_list).split(':')
            minutes = int(time.pop(1))
            minutes += randint(1, 59)
            time.append(str(minutes))
            return ','.join(time)

        # if category_key:
        #     testing_cats = input(f'Choose a category')

        self.test.clear()
        for i in range(days):
            day = {k: testtime((self.categories[k])) if 'TIME' in k else choice(self.categories[k]) for k in self.categories}
            self.test.append(day)

        if to_file:
            test_data_frame = pd.DataFrame(self.test)
            test_data_frame.to_csv(self.path_to_newtest, index=False)

        return self.test

