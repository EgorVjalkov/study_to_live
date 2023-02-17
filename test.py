from ComplexCondition import TestingPrices


test = TestingPrices('months/dec22test/FOR_TEST.csv', 'months/dec22test/price.csv')
test.read_and_filter()
print(test.create_a_testframe(20))

comparison_dict = {'<': lambda x, y: x < y,
                        '<=': lambda x, y: x <= y,
                        '>=': lambda x, y: x >= y,
                        '>': lambda x, y: x > y}

