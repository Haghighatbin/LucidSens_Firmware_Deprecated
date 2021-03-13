from machine import RTC, Pin, SPI, DHT
from utime import strftime, sleep, localtime
import display

tft = display.TFT()
tft.init(tft.ST7735R, speed=10000000, spihost=tft.VSPI, mosi=23, miso=19, clk=18, cs=5, dc=15, rst_pin=14, hastouch=False, bgr=False, width=128, height=128)

day = strftime('%a', localtime())
date = strftime('%d-%b-%Y', localtime())
init_x, init_y = 2, 3
maxx, maxy = tft.screensize()

def frame():
  tft.rect(init_x, init_y, maxx, maxy, color=tft.RED)

def write(font, txt, color, x=init_x + 1, y=init_y + 1):
  tft.font(font)
  tft.text(x, y, txt, color)

tft.clear()


write('FONTS/font10B.fon', txt=date, color=tft.GREEN, x=init_x + 32, y=init_y + 100)
tft.rect(init_x + 28,init_y + 99, 72, 12, color=tft.BLUE)

write('FONTS/font10B.fon', txt=strftime('%H:%M', localtime()), color=tft.GREEN, x=init_x + 50, y=init_y + 114)
tft.rect(init_x + 47, init_y + 112, 35, 12, color=tft.BLUE)

write('FONTS/font72.fon', txt='55', color=tft.RED, x=init_x + 5, y=init_y + 27)
write('FONTS/font10.fon', txt='o', color=tft.RED, x=init_x + 78, y=init_y + 27)
write('FONTS/font20B.fon', txt='C', color=tft.RED, x=init_x + 85, y=init_y + 32)

tft.image(init_x + 104, init_y + 3, 'ICONS/wifi.jpg', 2, tft.JPG) # Slot 1
tft.rect(init_x + 104, init_y + 3, 22, 22, color=tft.BLUE)

tft.rect(init_x + 80, init_y + 3, 22, 22, color=tft.BLUE) 
tft.rect(init_x + 56, init_y + 3, 22, 22, color=tft.BLUE)
tft.rect(init_x + 32, init_y + 3, 22, 22, color=tft.BLUE)
tft.rect(init_x + 8, init_y + 3, 22, 22, color=tft.BLUE)

tft.image(init_x + 100, init_y + 77, 'ICONS/humidity.jpg', 2, tft.JPG)
write('FONTS/font10B.fon', txt='55%', color=tft.WHITE, x=init_x + 103, y=init_y + 65)
tft.rect(init_x + 102, init_y + 62, 24, 14, color=tft.BLUE)

tft.rect(init_x + 7, init_y + 27, 93, 65, fillcolor=tft.BLACK)
tft.image(init_x + 7, init_y + 27, 'ICONS/wait.jpg', 0, tft.JPG)


