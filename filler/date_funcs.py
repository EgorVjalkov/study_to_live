import datetime
from typing import Optional


def today():
    return datetime.date.today()


def today_for_filling(date: Optional[datetime.date] = None) -> datetime.date:
    now = datetime.datetime.now()
    if  0 <= now.hour < 6:
        # кароч, время заполнения расширяется. Хоть и более нуля, но все равнр прошой датой
        return now.date() - datetime.timedelta(days=1)
    else:
        return now.date()


def yesterday(today_: datetime.date):
    return today_ - datetime.timedelta(days=1)


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


def is_same_months(day_dict: dict) -> bool:
    return day_dict['s'].month == day_dict['f'].month


dd = get_dates_dict(today(), before=7, after=7)
print(dd)

