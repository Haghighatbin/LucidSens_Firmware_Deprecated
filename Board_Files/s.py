import sys, machine, utime, _thread
import o
from upysh import clear
import ujson as json


class SerialConnection:
    def __init__(self):
        self.read = ''
        self.signal = ''
        self.content = ''
        self.opr = o.Operator()
        self.clear = clear

    def read_until(self, ending, timeout=10000):
        try:
            self.read = machine.stdin_get(1, timeout)
            if self.read is None:
                self.read = ''
            else:
                pass
            timeout_count = 0
            while True:
                if self.read is not None:
                    if self.read.endswith(ending):
                        break
                    else:
                        new_data = machine.stdin_get(1, timeout)
                        self.read += new_data
                        timeout_count = 0
                elif self.read is None:
                    # print('read is None')
                    break
                else:
                    timeout_count += 1
                    if timeout is not None and timeout_count >= timeout:
                        break
        except:
            pass
        return self.read

    def sr_handler(self, cmd):
        self.opr.operator_func(cmd)
        return

    def sr_receiver(self):
        self.clear
        while True:
            try:
                # print('sr_thread: sending READY signal.')
                # machine.stdout_put('s_thread: READY.\n')
                # utime.sleep(1)
                # while 'go#' not in self.read_until('#'):
                while 'go#' not in self.signal and '!#' not in self.signal:
                    machine.stdout_put('s_thread: READY.\n')
                    utime.sleep(2)
                    self.signal = self.read_until('#')

                if '!#' in self.signal:
                    print('aborted by user.')
                    break
                else:
                    machine.stdout_put('got it!\n')
                    self.clear

                while '*' not in self.content:
                    try:
                        data = self.read_until('#')
                        # print(data)
                        if '#' in data and data[:-2] not in self.content:
                            if data[-2] == '*':
                                self.content += data[:-1]
                                break
                            elif data[-2] == '_':
                                self.content += data[:-2]
                                machine.stdout_put('got it!\n')
                            else:
                                utime.sleep(1)
                                pass
                        else:
                            pass
                    except:
                        break
                utime.sleep(1)
                if '*' in self.content:
                    machine.stdout_put('EOF received.\n')
                    # print('Content: {}\n'.format(content))
                    # print('length: {} chars\n'.format(len(content)))
                    print('saving cmd file\n')
                    raw_cmd = open('cmd.txt', 'w')
                    raw_cmd.write(self.content[:-1])
                    raw_cmd.close()
                    resp = open('cmd.txt', 'r')
                    print('evaling cmd in resp.\n')
                    for line in resp:
                        cmd = eval(line)
                        self.sr_handler(cmd)
                    resp.close()
                    print('closed resp.\n')
            except KeyboardInterrupt:
                print('Keyboard interrupt')
                sys.exit(0)
            except Exception as e:
                print(e)
                break

    def __str__(self):
        return "Serial connection is established."
