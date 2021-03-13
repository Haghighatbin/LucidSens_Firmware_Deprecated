import _thread, sys
import one, two, three


def one_thread():
    print('thread_1 initiates')
    _thread.allowsuspend(True)
    one.run()


def two_thread():
    print('thread_2 initiates')
    _thread.allowsuspend(True)
    two.run()


def three_thread():
    print('thread_3 initiates')
    _thread.allowsuspend(True)
    three.run()


def main():
    # _thread.start_new_thread(print_time, ("Thread-1", 2,))
    _thread.start_new_thread('thread_1', one_thread, ())
    _thread.start_new_thread('thread_3', three_thread, ())
    _thread.start_new_thread('thread_2', two_thread, ())


if __name__ == '__main__':
    main()
