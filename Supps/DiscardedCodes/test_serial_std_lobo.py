import time
import sys
from upysh import *


def read_until(ending, timeout=10000):
    read = machine.stdin_get(1, timeout)
    timeout_count = 0
    try:
        while True:
            if read is not None:
                if read.endswith(ending):
                    break
                else:
                    new_data = machine.stdin_get(1, timeout)
                    read += new_data
                    timeout_count = 0
            else:
                timeout_count += 1
                if timeout is not None and timeout_count >= timeout:
                    break
    except KeyboardInterrupt:
        print('aborted.')
    except:
        pass
    return read


try:
    print('listening...\n')
    content = ''
    while '*' not in content:
        try:
            data = read_until('#')
            if '#' in data and data[:-1] not in content:
                content += data[:-1]
                machine.stdout_put('got it!\n')
                time.sleep(1)
            else:
                pass
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            break
    if '*' in content:
        machine.stdout_put('end of file received\n')

        print('Content: {}\n'.format(content))
        print('length: {} chars\n'.format(len(content)))
        # print('saving file')
        f = open('recvd.txt', 'w')
        f.write(content[:-1])
        f.close()
        print('file saved.')
except KeyboardInterrupt:
    print('aborted.')
except Exception as e:
    print(e)
