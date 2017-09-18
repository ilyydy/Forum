import time


def log(*args, **kwargs):
    '''
    输出信息到 界面和 log.txt
    '''
    # time.time() 返回 unix time
    # 把 unix time 转换为格式化字符串
    format = '%H:%M:%S'
    value = time.localtime(int(time.time()))
    dt = time.strftime(format, value)
    with open('log.txt', 'a', encoding='utf-8') as f:
        print(dt, *args, **kwargs)
        print(dt, *args, file=f, **kwargs)
