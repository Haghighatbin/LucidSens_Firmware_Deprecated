import time
import _thread


def run():
    while True:
      ntf = _thread.getnotification()
      if ntf == _thread.EXIT:
        print('thread three received EXIT.')
        break

      time.sleep(3)
      print('thread 3 is running.')
