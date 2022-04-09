from datetime import datetime
import time,os


def stamp2time(timestamp):
    try:
        k = len(str(timestamp)) - 10
        timestamp = datetime.fromtimestamp(timestamp / (1 * 10 ** k))
        timestr = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
        return timestr[:-3]
    except Exception as e:
        print(e)
        return [False,str(e)]

def newfolder(fodlerpath):
    if not os.path.exists(fodlerpath):
        os.mkdir(fodlerpath)
        print(f'[log] create {fodlerpath} successfully!')


if __name__ == '__main__':
    nowtime =stamp2time(int(time.time() * 1000)).replace(':', '_').replace(' ', '_')
    print(nowtime)