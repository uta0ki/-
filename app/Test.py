import time

def demo(day1, day2):
    time_array1 = time.strptime(day1, "%Y-%m-%d %H:%M")
    timestamp_day1 = time.mktime(time_array1)
    time_array2 = time.strptime(day2, "%Y-%m-%d %H:%M")
    timestamp_day2 = time.mktime(time_array2)
    result = (timestamp_day2 - timestamp_day1) // 60
    return result

day1 = "2020-09-26 10:01"
day2 = "2020-09-26 10:10"

day_diff = demo(day1, day2)
print("两个日期的间隔分钟：{} ".format(day_diff))
