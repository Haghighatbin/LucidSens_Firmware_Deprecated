import sys
import serial
import serial.tools.list_ports as lp
import time
import json
import random


# chars = '0987654321qwertyuiopasdfghjklzxcvbnm{}[]=-+QWERTYUIOPASDFGHJKLZXCVBNM,'
# pck_size = 79  # 15: 64 byte, 79:128 byte, 207: 256 byte,463: 512 byte, 975: 1024 byte ---> 49

# def random_string(size):
#     return ''.join(random.choice(chars) for _ in range(size))


def dict_gen(n):
    values = ['value1', 'value2']
    mydict = {"key " + str(i): values[0] for i in range(n)}
    mydict["key " + str(random.randrange(n))] = values[1]

    return mydict


def chunker_func(cmd):
    data = []
    segments = [cmd[i:i + packet_size] for i in range(0, len(cmd), packet_size)]
    for segment in segments:
        if segment == segments[-1]:
            data.append(segment + '*#')
        else:
            data.append(segment + '_#')
    return data


def srl_finder():
    # port_serial = ''
    if lp.comports():
        for idx, ports in enumerate(lp.comports()):
            # print(ports.device)
            if "usbmodem" in str(ports.device) or "wch" in str(ports.device) or "SLAB" in str(ports.device):
                return str(ports.device)
                # print(port_serial)
            #     port_serial = port_serial.replace("cu", "tty")


packet_size = 77
pck = json.dumps(dict_gen(100))
delay = 2
operator = serial.Serial(srl_finder(), baudrate=115200)
print('waiting for the signal...')
while b's_thread:ready to read cmd...' not in operator.read_all():
    time.sleep(delay)
print('got the the request signal, sending GO!')
operator.write('go#'.encode())
time.sleep(2)
pck_size_tot = 0
t0 = time.time()

for idx, data in enumerate([chunk for chunk in chunker_func(pck)]):
    print('packet[{}]: {} --- length: {} chars --- size: {}'.format(idx, data, len(data), sys.getsizeof(data)))
    operator.write(data.encode())
    time.sleep(delay)
    resp = operator.read_all()
    if 'EOF received.' in resp.decode():
        print('EOF received in first run, file was sent successfully.')
    elif b'got it!' in resp:
        print('packet [{}] received on the first try.'.format(idx))
        pck_size_tot += sys.getsizeof(data)
    else:
        while True:
            print('sending packet again: {}'.format(data))
            operator.write(data.encode())
            time.sleep(delay)
            resp = operator.read_all()
            if b'got it!' in resp:
                print('packet sent in retry.')
                pck_size_tot += sys.getsizeof(data)
                break
            elif 'EOF received' in resp.decode():
                print('EOF received in retry')
                pck_size_tot += sys.getsizeof(data)
                break
            else:
                time.sleep(5)
                pass
        print('packet received eventually.')

print('it took {} seconds for {} bytes to be transferred.'.format((time.time() - t0), pck_size_tot))
print('Done!')
