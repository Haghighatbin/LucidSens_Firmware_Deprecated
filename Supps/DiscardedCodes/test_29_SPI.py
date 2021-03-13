from machine import Pin, SPI
import time
# sck -- mosi -- miso -- cs
# SPI1: 6, 8, 7, 11
# 1: HSPI: 14,13,12,15
# 2: VSPI: 18,23,19, 5

# VSPI is not available if the psRAM is configured to run at 80 MHz.
# check the PSRAM frequency
# see if you can switch to HSPI
# Pin 15 is on HSPI!!!
# if psRAM is used with ESP32, and is set to run at 80MHz,
# VSPI is not available to the user, as it is used by psRAM driver!!
# and eventually you can use ADC of ESP32 (Voltage 0 - 1V)
# use LDR, lower down the input current

# spi = SPI(2, miso=19, mosi=23, sck=18)
sck = Pin(18)
miso = Pin(19)
mosi = Pin(23)
spi = SPI(2, miso=miso, mosi=mosi, sck=sck)

pwr = Pin(2, Pin.OUT) # change this
#g0 = Pin(4, Pin.INOUT)
#g1 = Pin(22, Pin.INOUT)
#spd = Pin(2, Pin.INOUT)
pwr.value(1)
#g0.value(0)
#g1.value(0)
#spd.value(0)
gain = 1
Vref = 5
# 8388607
try:
  while True:
    recvd = spi.read(3)
    int_val = int.from_bytes(recvd, 'big')
    print('non-processed: {:.2f} V'.format(int_val * (Vref/2) / (524287 * gain)))
    resp = (((recvd[0] & 0x07) << 16) + (recvd[1] << 8) + (recvd[2] & 0xFF))
    print('processed: {:.2f} V'.format(resp * (Vref/2) / (524287 * gain)))
    print('#----#')
    time.sleep(0.2)
except:
  #g0.value(0)
  #g1.value(0)
  pwr.value(0)
  spi.deinit()
  print('gains and power are all down')

