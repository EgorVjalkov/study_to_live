from random import choice


ABC = list('qwertyuiopasdfghjklzxcvbnm')
special = list('()[]{}\'"\?:;-_=+!@#$%^&*/|')
numbers = list('1234567890')

all_marks = ABC + special + numbers
print(all_marks)

def new_test(num):
    test_list = []
    for i in range(num):
        mark = choice(all_marks)
        test_list.append(mark)
    lesson = ' '.join(test_list)
    if input('  ' + lesson + '\n: ') == lesson:
        print('correct')
    else:
        print('mistakes')

new_test(2)
