import time
import _thread


def run():
    while True:
        ntf = _thread.getnotification()
        if ntf == _thread.EXIT:
            print('thread one received EXIT.')
            return

        time.sleep(1)
        print('thread 1 is running.')

