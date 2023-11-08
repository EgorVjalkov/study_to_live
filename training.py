import datetime
list_ = []


def decorator_f(func):
    def wrapper(args):
        res = func(args)
        list_.append(res)
    return wrapper


@decorator_f
def print_(str):
    print(str)
    return str


print_('1')
print_('1')
print_('1')
print_('1')
print(list_)

today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
print(today, yesterday)
