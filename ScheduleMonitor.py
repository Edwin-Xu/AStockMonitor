# coding=UTF-8
# 调度监控
import time

from AMonitor import *
from time import strftime, localtime

if __name__ == '__main__':
    # 请求一分钟，每次睡眠4分钟，差不多5分钟提醒一次
    M = 60
    sleep_time = 4 * M

    while (True):
        print(strftime('%Y-%m-%d %H:%M:%S', localtime()))
        now = datetime.datetime.now()
        weekday = now.weekday()
        minute = now.minute + now.hour * M
        # 如果是周末，则睡眠4小时
        if 6 <= weekday <= 7:
            time.sleep(4 * 60 * M)
            continue
        # 交易中
        elif 9 * M + 30 <= minute < 11 * M + 30 or 13 * M <= minute < 15 * M:
            monitor(None, 'all', '5m', 4, -20)
            time.sleep(sleep_time)
        # 如果是9点前、15点后、12点半前，则每次睡眠0.5小时
        elif minute < 9 * M or minute < 12 * M + 30 or minute >= 15 * M:
            time.sleep(30 * M)
            continue
        # 上下午开盘前30分钟，只睡眠1分钟
        else:
            time.sleep(1 * M)
            continue
