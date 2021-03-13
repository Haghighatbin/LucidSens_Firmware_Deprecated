import sys
import o
from upysh import *
import ujson as json
from machine import UART
from time import sleep


class SerialConnection:
    def __init__(self):
        self.opr = o.Operator()
        self.uart = UART(1, baudrate=9600, bits=8, parity=None, stop=1, tx=12, rx=14, rts=-1, cts=-1, txbuf=256,
                         rxbuf=256, timeout=100, timeout_char=2)
        self.clear = clear

    def sr_handler(self):
        while True:
            try:
                # cmd = sys.stdin.read(57).strip()
                self.clear
                print('\ns_thread: waiting for the incoming calls...')
                cmd = ''
                while True:
                        read = sys.stdin.read(1)
                        print("uart is waiting for: {} --- read {} and type is:{}".format(self.uart.any(), read, type(read)))
                        if read == '{' or '{' in cmd:
                            cmd += read
                            if len(cmd) > 2 and cmd[-3] == '#':
                                break
                            if read == '*':
                                cmd += read
                                break
                        else:
                            pass
                if '*' in cmd:
                    print('\ns_thread: aborted!')
                    break
                print(cmd, type(cmd))
                if all(_ in str(cmd) for _ in ['header', 'body', '#']):
                    jsnd_cmd = json.loads(cmd)
                    print('json created!')
                    print(self.opr.operator_func(jsnd_cmd))
                else:
                    print("what received is: {} --- {}".format(type(cmd), cmd))

            except KeyboardInterrupt:
                print('\ns_thread: aborted!')
                break
                # sys.exit(0)
            except Exception as e:
                print(e)
                pass

    def __str__(self):
        print("SerialConn class is activated.")
from machine import UART
from time import sleep

uart = UART(1, 9600) 
uart.init(9600, bits=8, parity=None, stop=1)
while not uart.any():
  pass
sleep(400)
content = uart.readall()
uart.init(baudrate = 115200)
print(content)




