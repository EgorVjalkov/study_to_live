import datetime


today: datetime.date = datetime.date.today()
yesterday: datetime.date = today - datetime.timedelta(days=1)
week_before_day = today - datetime.timedelta(days=7)

