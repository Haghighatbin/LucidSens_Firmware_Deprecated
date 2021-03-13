from machine import RTC, Pin, I2C
from ssd1306 import SSD1306_I2C
import f10, f20, f40
from Board_Files.writer import Writer
from utime import strftime, localtime

sda_pin = Pin(21)
scl_pin = Pin(22)
i2c = I2C(scl=scl_pin, sda=sda_pin)
oled = SSD1306_I2C(128, 64, i2c)

rtc = RTC()
print('Syncing NTP...')
rtc.ntp_sync(server='cn.pool.ntp.org', tz='CST-8')

def write(font=f10, txt='OLED Available!', x=0, y=0):
    w = Writer(oled, font, verbose=False)
    Writer.set_clip(True, True)
    Writer.set_textpos(x, y)
    w.printstring(txt)
    oled.show()
oled.fill(0)
oled.show()

now_time = localtime()
#print('time')
time = strftime('%H:%M', now_time)
day = strftime('%a', now_time)
date = strftime('%d-%b-%Y', now_time)

    
write(font=f40, txt='27', x=2, y=25)
write(font=f20, txt='C', x=4, y=78)
write(font=f10, txt='o', x=2, y=73)
write(font=f10, txt=day, x=5, y=5)
write(font=f10, txt=date, x=38, y=29)
write(font=f10, txt=time, x=50, y=45)
write(font=f20, txt='83', x=40, y=93)
write(font=f10, txt='%', x=50, y=118)

for x in range(45):
  for y in range(35):
    oled.pixel(x + 25, y + 2, 1)
    
for x in range(30):
  for y in range(10):
    oled.pixel(x + 45, y + 50, 1)
    
for x in range(23):
  for y in range(20):
    oled.pixel(x + 93, y + 40, 1)
