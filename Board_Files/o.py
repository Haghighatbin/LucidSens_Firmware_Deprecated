import ujson as json
import machine
import utime
import sys
from upysh import *


class Operator:
    def __init__(self):
        self.clear = clear
        self.machine = machine
        self.seg_size = 510

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
        except KeyboardInterrupt:
            # print('aborted.')
            sys.exit(0)
        except:
            pass
        return self.read

    def sender(self, response):
        def chunker(cmd):
            # return [cmd[i:i + self.pck_size] for i in range(0, len(cmd), self.pck_size)]
            data = []
            segments = [cmd[i:i + self.seg_size] for i in range(0, len(cmd), self.seg_size)]
            for segment in segments:
                if segment == segments[-1]:
                    data.append(segment + '*#')
                else:
                    data.append(segment + '_#')
            return data
        self.clear
        try:
            if len(response) > self.seg_size:
                # for idx, data in enumerate([chunk for chunk in chunker(response)]):
                for data in ([chunk for chunk in chunker(response)]):
                    self.machine.stdout_put(data)
                    utime.sleep(1)
                    resp = self.read_until('#', 5000)
                    if 'EOF received.\n' in resp:
                        pass
                    elif 'got it!\n' in resp:
                        pass
                    else:
                        while True:
                            self.machine.stdout_put(data)
                            utime.sleep(1)
                            resp = self.read_until('#', 5000)
                            if 'EOF received.\n' in resp:
                                break
                            elif 'got it!\n' in resp:
                                break
                            else:
                                utime.sleep(2)
                                pass
            else:
                self.machine.stdout_put(response)
                utime.sleep(2)
                resp = self.read_until('#', 5000)
                if 'EOF received.\n' in resp:
                    pass
                elif 'got it!\n' in resp:
                    pass
                else:
                    while True:
                        self.machine.stdout_put(response)
                        utime.sleep(1)
                        resp = self.read_until('#', 5000)
                        if 'got it!' in resp:
                            break
                        elif 'EOF received.\n' in resp:
                            break
                        else:
                            utime.sleep(2)
                            pass
            utime.sleep(1)

        except KeyboardInterrupt:
            print('Aborted!')
        except Exception as e:
            print(e)

    def operator_func(self, command):
        if command['header'] == 'test':
            import test_A
            asteroid = test_A.TestAsteroid()
            resp = open('resp.txt', 'w')
            resp.write(asteroid.test_asteroid(command['body']['it']))
            resp.close()
            r = open('resp.txt', 'r')
            for line in r:
                self.sender(line)
            return

        if command['header'] == 'run':
            if command['body']['it'] is not None:
                from drv8825_esp32_gpio import DRV8825
                drvr = DRV8825(33, 32, 25, 26, 27)
                response = ({'header': 'run_incubator'}, {'body': 'incubation initialized.'})
                print(json.dumps(response))
                drvr.incubation_mode('Full', command['body']['it'], 0)
                return

    def __str__(self):
        print("Operator class is activated.")
