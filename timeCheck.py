from datetime import datetime


def is_between(startTime, endTime, nowTime):
    endTime = datetime.strptime(endTime, "%H:%M")
    startTime = datetime.strptime(startTime, "%H:%M")
    nowTime = datetime.strptime(nowTime, "%H:%M")

    if startTime < endTime:
        return nowTime >= startTime and nowTime <= endTime
    else:  # Over midnight
        return nowTime >= startTime or nowTime <= endTime


timeStart = "15:00"
timeEnd = "16:00"
timeNow = "15:59"
# timeEnd = datetime.strptime(timeEnd, "%H:%M")
# timeStart = datetime.strptime(timeStart, "%H:%M")
# timeNow = datetime.strptime(timeNow, "%H:%M")
#
print(is_between(timeStart, timeEnd, timeNow))
