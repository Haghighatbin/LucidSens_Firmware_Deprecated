import sys
import o
from upysh import *
import ujson as json
from time import sleep


class SerialConnection:
    def __init__(self):
        self.opr = o.Operator()
        self.clear = clear

    def sr_handler(self):
        while True:
            try:
                # cmd = sys.stdin.read(57).strip()
                self.clear
                cmd = ''
                while True:
                    read = sys.stdin.read(1)
                    if read == '{' or '{' in cmd:
                        cmd += read
                    if len(cmd) > 2 and cmd[-3] == '#':
                        break
                    if read == '*':
                        cmd += read
                        break
                if '*' in cmd:
                    print('\ns_thread: aborted!')
                    break
                if all(_ in str(cmd) for _ in ['header', 'body', '#']):
                    jsnd_cmd = json.loads(cmd)
                    print('json created!')
                    print(self.opr.operator_func(jsnd_cmd))
                else:
                    print("what received is: {} --- {}".format(type(cmd), cmd))

            except KeyboardInterrupt:
                print('\ns_thread: aborted!')
                # break
                # sys.exit(0)
            except Exception as e:
                # print(e)
                pass

    def __str__(self):
        print("SerialConn class is activated.")
