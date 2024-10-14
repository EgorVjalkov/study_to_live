import datetime
from typing import Optional


def get_month(date: datetime.date) -> str:
    return date.strftime('%b%y').lower()


def now():
    return datetime.datetime.now()


def today():
    return datetime.date.today()

def tomorrow(date: datetime.date):
    return date + datetime.timedelta(days=1)

#print(tomorrow(datetime.date.today()))


def today_for_filling(now_: Optional[datetime.datetime] = None) -> datetime.date:
    if not now_:
        now_ = now()

    if 0 <= now_.hour < 6:
        # кароч, время заполнения расширяется. Хоть и более нуля, но все равнр прошой датой
        return now_.date() - datetime.timedelta(days=1)
    else:
        return now_.date()

def yesterday(today_: datetime.date):
    return today_ - datetime.timedelta(days=1)


def week_before_(day: datetime.date):
    return day - datetime.timedelta(days=7)


def last_date_of_past_month(date: datetime.date):
    first_date_of_month = datetime.date(day=1, month=date.month, year=date.year)
    return first_date_of_month - datetime.timedelta(days=1)


def get_dates_list(date: datetime.date,
                   before: int = 0,
                   after: int = 0) -> list:
    dates_range = range(before, after+1, 1)
    #print(dates_range)
    dates_list = [date+datetime.timedelta(days=i) for i in dates_range]
    return dates_list


#print(get_dates_list(datetime.date.today(), -7, 7))


def is_same_months(days: list) -> bool:
    return days[0].month == days[-1].month


#dd = get_dates_dict(today(), before=7, after=7)
#print(dd)

