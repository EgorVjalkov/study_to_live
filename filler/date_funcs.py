import datetime


def today():
    return datetime.date.today()


def yesterday():
    return today() - datetime.timedelta(days=1)


def week_before_(day: datetime.date):
    return day - datetime.timedelta(days=7)
