import datetime


def today():
    return datetime.date.today()


def yesterday():
    return today() - datetime.timedelta(days=1)


def week_before_(day: datetime.date):
    return day - datetime.timedelta(days=7)


def last_date_of_past_month(date: datetime.date):
    first_date_of_month = datetime.date(day=1, month=date.month, year=date.year)
    return first_date_of_month - datetime.timedelta(days=1)


def get_dates_dict(date: datetime.date,
                   before: int = 0,
                   after: int = 0) -> dict:
    dates = {'s': date - datetime.timedelta(days=before),
             'f': date + datetime.timedelta(days=after)}
    return dates


print(get_dates_dict(today(), before=7, after=7))

