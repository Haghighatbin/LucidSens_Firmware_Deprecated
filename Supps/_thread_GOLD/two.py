import time
import _thread


def run():
    while True:
        time.sleep(10)
        print('thread 2 sending Exit notification to thread 1 and 3.')
        print(_thread.list())
        print('EXIT sender thread is {}'.format(_thread.getSelfName()))
        print('list of active threads:')
        threads = _thread.list(False)
        for thrd in threads:
            #print(thrd[2])
            if thrd[2] == 'thread_1':
              print("closing thread_1")
              _thread.notify(thrd[0], _thread.EXIT)
              print('thread_1 is now closed')
              time.sleep(1)
            elif thrd[2] == 'thread_3':
              print("closing thread_3")
              _thread.notify(thrd[0], _thread.EXIT)
              print('thread_3 is now closed.')
              time.sleep(1)
        print('now closing thread_2')
        _thread.EXIT
        break
    print("all threads are now closed.")
    return
