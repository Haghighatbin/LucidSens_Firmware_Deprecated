from machine import UART
import time
from upysh import *
import w_lobo

time.sleep(5)

uart = UART(2, tx=17, rx=16)
uart.init(115200, bits=8, parity=None, stop=1)

try:
  content = ''
  while True:
    data = uart.read()
    print(uart.any())
    if data is not None:
      print('got something -> {}'.format(data.decode()))
      content += data.decode()
    if data == b'\n':
      print('breaking now')
      break
    print('data: [{}]'.format(data.decode()))
    time.sleep(2)
#  while not uart.any():
#    pass
#  if uart(any):
#    print(uart.any())
#    content = uart.readline()
#    uart.init(baudrate=115200)
  print('saving the file')
  f = open('recvd.txt', 'w')
  f.write(str(content))
  f.close()
  print('done')
except KeyboardInterrupt:
    print('aborted!')
except Exception as e:
    print(e)






