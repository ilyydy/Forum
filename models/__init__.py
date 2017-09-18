import datetime
import time


def timestamp():
    return int(time.time())


def datetime_delta(time):
    '''
    根据传入的时间戳返回距离现在的日常表示时间字符串
    '''
    now = timestamp()
    seconds = now - time
    days = int(seconds / 3600 / 24)
    months = int(days / 30)

    if days < 30:
        if seconds < 60:
            return '几秒前'
        elif seconds < 3600:
            return '{}分钟前'.format(int(seconds/60))
        elif days < 1:
            return '{}小时前'.format(int(seconds/3600))
        else:
            return '{}天前'.format(days)
    else:
        return '{}月前'.format(months)
