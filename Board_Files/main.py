import w, s
import gc
import _thread
_thread.stack_size(3*4096)
print('THREAD stack_size is: {}'.format(_thread.stack_size()))
from tft import ScrST7735
from time import sleep
from drv8825 import DRV8825
from machine import Pin
p14 = Pin(14, Pin.OUT, value=0)
p15 = Pin(15, Pin.OUT, value=0)
p5 = Pin(5, Pin.OUT, value=0)
print('Pins 4, 14, 15 are all down now.')

green = '\033[92m'
red = '\033[91m'
cyan = '\033[96m'
pink = '\033[95m'
yellow = '\033[93m'
white = '\033[97m'


def main():
    # gc.enable()
    def gc_thrd():
        _thread.allowsuspend(True)
        while True:
            ntf = _thread.getnotification()
            if ntf == _thread.EXIT:
                print('GC thread received EXIT command.')
                return
            gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
            if gc.mem_free() < gc.threshold():
                gc.collect()
                print('available memory now: {}'.format(gc.mem_free()))
            sleep(10)
    try:
        tft = ScrST7735()
        tft.clear()
        tft.welcome(True)
        tft.connect_status()
        tft.serial_status(False)
        tft.temp_status()
        tft.welcome(False)
        tft.frame()

        print('establishing wifi connection.')
        wf = w.WifiConnection()
        if wf.wf_connection():
            tft.wifi_status(True)
            print(yellow + "WIFI is connected." + green)
            # wf_thrd = _thread.start_new_thread('wifi_thread', wf.wf_handler, ())
        else:
            wf.wf_disconnect()
            print(red + 'wifi is not connected.' + green)
            tft.wifi_status(False)

        tft.hv_panel(True)

        print('initializing the stepper.')
        tft.opr_status('stepper')
        stpr = DRV8825(13, 33, 32, 35)
        stpr.interrupter()
        print(red + 'stepper adjusted to zero-point.' + green)
        tft.opr_status('done')

        # print('activated threads:\n')
        # print('\n'.join(pink + str(thrd) + green for thrd in _thread.list(False)))

        print('establishing serial connection.')
        sr = s.SerialConnection()
        tft.serial_status(True)

        gc_thrd = _thread.start_new_thread('gc_thrd', gc_thrd, ())
        print(cyan + 'GC thread is activated.' + green)
        sleep(1)
        status_thrd = _thread.start_new_thread('status_thrd', tft.status_thrd, ())
        sleep(1)
        print(cyan + 'STATUS thread activated.' + green)
        sleep(1)
        print(cyan + 'SERIAL thread is activated.' + green)
        serial_thrd = _thread.start_new_thread('serial_thrd', sr.sr_receiver, ())

    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(e)
        print(red + 'main module interrupted.' + green)


if __name__ == '__main__':
    main()
