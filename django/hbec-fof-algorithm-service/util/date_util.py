import datetime
import time
from datetime import date


def count_days(year, month, day):
    date = datetime.date(year, month, day)
    return date.strftime('%j')


def count_current_days():
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    day = now.day
    return count_days(year, month, day)


def formatDate2yyyymmdd():
    now = int(time.time())
    timeStruct = time.localtime(now)
    return time.strftime("%Y%m%d", timeStruct)


def compute_time(start_time):
    seconds, minutes, hours = int(time.time() - start_time), 0, 0
    hours = seconds // 3600
    minutes = (seconds - hours * 3600) // 60
    seconds = seconds - hours * 3600 - minutes * 60
    return hours, minutes, seconds


def getQunian():
    y = datetime.datetime.now().year - 1
    return str(y) + '1231'


def getQiannian():
    y = datetime.datetime.now().year - 2
    return str(y) + '1231'


def convertstringtodate(stringtime):
    if stringtime[0:2] == "20":
        year = stringtime[0:4]
        month = stringtime[4:6]
        day = stringtime[6:8]
        begintime = date(int(year), int(month), int(day))
        return begintime
    else:
        year =  stringtime[0:4]
        month = stringtime[4:6]
        day = stringtime[6:8]
        begintime = date(int(year), int(month), int(day))
        return begintime


def comparetime(nowtime, stringtime):
    if isinstance(nowtime, date):
        pass
    else:
        nowtime = convertstringtodate(nowtime)
    if isinstance(stringtime, date):
        pass
    else:
        stringtime = convertstringtodate(stringtime)
    result = nowtime - stringtime
    return result.days
