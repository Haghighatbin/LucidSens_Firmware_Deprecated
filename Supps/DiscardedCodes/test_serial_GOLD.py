import time
import sys
from upysh import *
import machine

def read_until(ending, timeout=10000):
    try:
        read = machine.stdin_get(1, timeout)
        if read is None:
          read = ''
        else:
          pass
        timeout_count = 0
        while True:
            if read is not None:
                if read.endswith(ending):
                    break
                else:
                    new_data = machine.stdin_get(1, timeout)
                    read += new_data
                    timeout_count = 0
            elif read is None:
              #print('read is None')
              break
            else:
                timeout_count += 1
                if timeout is not None and timeout_count >= timeout:
                    break
    except KeyboardInterrupt:
        #print('aborted.')
        sys.exit(0)
    except:
        pass
    return read


try:
    print('listening...')
    while 'go#' not in read_until('#'):
      machine.stdout_put('s_thread:ready to read cmd...')
      time.sleep(2)
    #print('got the GO signal.')
    clear
    content = ''
    while '*' not in content:
        try:
            data = read_until('#')
            if '#' in data and data[:-1] not in content:
                content += data[:-1]
                machine.stdout_put('got it!')
                time.sleep(1)
            else:
                pass
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            break
    if '*' in content:
        machine.stdout_put('EOF received.')

        #print('Content: {}\n'.format(content))
        #print('length: {} chars\n'.format(len(content)))
        # print('saving file')
        f = open('recvd.txt', 'w')
        f.write(content[:-1])
        f.close()
        print('file saved.')
except KeyboardInterrupt:
    print('aborted.')
except Exception as e:
    print(e)



