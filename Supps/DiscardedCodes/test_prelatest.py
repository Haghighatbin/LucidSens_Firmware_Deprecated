import time
import sys
from upysh import *


def read_until(ending):
    read = sys.stdin.read(1)
    try:
        while True:
            if read is not None:
                if read.endswith(ending):
                    break
                else:
                    new_read = sys.stdin.read(1)
                    read += new_read
            else:
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
                sys.stdout.write('got it!\n')
                time.sleep(1)
            else:
                pass
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            break
    if '*' in content:
        sys.stdout.write('EOF received.\n')
        time.sleep(1)
        print('Content: {}\n'.format(content))
        print('length: {} chars\n'.format(len(content)))
        # print('saving file')
        f = open('recvd.txt', 'w+')
        f.write(content[:-1])
        f.close()
        print('file saved.')
except KeyboardInterrupt:
    print('aborted!')
except Exception as e:
    print(e)
