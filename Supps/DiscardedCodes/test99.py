from machine import Pin, SPI
import time
"""
g0 g1 -- 0,0 -- gain: 1
g0 g1 -- 1,0 -- gain: 2
g0 g1 -- 0,1 -- gain: 64
g0 g1 -- 1,1 -- gain: 128

"""
spi = SPI(2, miso=19, mosi=23, sck=18)
pwr = Pin(15, Pin.INOUT)# pwr
g0 = Pin(4, Pin.INOUT) # g0 
g1 = Pin(22, Pin.INOUT) # g1
spd = Pin(2, Pin.INOUT) # speed

pwr.value(1)
g0.value(1)
g1.value(1)
spd.value(0)

for _ in range(10):
  print(spi.read(3))
  time.sleep(0.2)

print("calibration is done.")
time.sleep(3)

while True:

  recvd = spi.read(3)
  int_val = int.from_bytes(recvd, 'big')
  
  print('non-processed: {:.2f} V'.format(int_val * 1.65 /8388607))
  
  resp = (((recvd[0] & 0x7f) << 16) + (recvd[1] << 8) + (recvd[2]))
  print('processed: {:.2f} V'.format(resp * 1.65 / 8388607))
  print('#----#')
  time.sleep(0.2)
  

