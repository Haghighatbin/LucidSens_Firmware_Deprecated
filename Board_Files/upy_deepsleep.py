import _thread
from machine import Pin, RTC, deepsleep
p25 = Pin(25, Pin.IN, Pin.PULL_DOWN)


def power_func():
    while True:
        if p25.value() == 1:
            RTC().wake_on_ext0(25, 1)
        else:
            deepsleep()


_thread.start_new_thread('power_switch', power_func, ())

