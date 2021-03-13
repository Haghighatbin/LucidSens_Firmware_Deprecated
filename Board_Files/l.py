from machine import RTC, Pin, I2C, DHT
from ssd1306 import SSD1306_I2C, const
import f10, f20, f40
from writer import Writer
from utime import strftime, sleep, localtime


class Oled:
    def __init__(self, scl_pin=22, sda_pin=21):
        self.WIDTH = const(128)
        self.HEIGHT = const(64)
        self.MARGIN = 1
        self.rtc = RTC()
        self.dht = DHT(Pin(27), DHT.DHT2X)
        self.fan = Pin(12, Pin.OUT)
        self.sda_pin = Pin(sda_pin)
        self.scl_pin = Pin(scl_pin)
        self.i2c = I2C(scl=scl_pin, sda=sda_pin)
        self.oled = SSD1306_I2C(self.WIDTH, self.HEIGHT, self.i2c)
        self.drop_shape = [
            [0, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 1, 1, 1, 1, 1, 0, 0],
            [0, 0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0, 0, 0],
        ]

    def scr_clear(self):
        self.oled.fill(0)
        self.oled.show()

    def sec_clear(self, a, b, i, j):
        for x in range(a):
            for y in range(b):
                self.oled.pixel(x + i, y + j, 0)
        self.oled.show()

    def write(self, font=f10, txt='OLED Available!', x=0, y=0):
        w = Writer(self.oled, font, verbose=False)
        Writer.set_clip(True, True)
        Writer.set_textpos(x, y)
        w.printstring(txt)
        self.oled.show()

    def hum_icon(self, x=2, y=2):
        for i, row in enumerate(self.drop_shape):
            for j, c in enumerate(row):
                self.oled.pixel(j + x, i + y, c)
        self.oled.show()

    def outline(self):
        for i in range(self.MARGIN, self.WIDTH - self.MARGIN):
            self.oled.pixel(i, self.MARGIN, 1)
            self.oled.pixel(i, self.HEIGHT - self.MARGIN, 1)
        for i in range(self.MARGIN, self.HEIGHT - self.MARGIN):
            self.oled.pixel(self.WIDTH - self.MARGIN, i, 1)
            self.oled.pixel(self.MARGIN, i, 1)
        self.oled.show()

    def ntp(self):
        if not self.rtc.synced:
            print('NTP not synced, re-syncing...')
            self.rtc.ntp_sync(server='cn.pool.ntp.org', tz='CST-8')
            sleep(2)

    def stats_thrd(self):
        self.scr_clear()
        self.outline()
        self.rtc.ntp_sync(server='cn.pool.ntp.org', tz='CST-8')
        sleep(1)
        self.write(font=f20, txt='C', x=4, y=106)
        self.write(font=f10, txt='o', x=2, y=101)
        self.write(font=f10, txt='%', x=50, y=116)
        self.hum_icon(x=116, y=38)
        while True:
            try:
                self.ntp()
                day = strftime('%a', localtime())
                date = strftime('%d-%b-%Y', localtime())
                sensor = self.dht.read()
                if sensor[0]:
                    temp, humid = sensor[1], int(sensor[2])
                else:
                    temp, humid = 25.1, 55
                if temp >= 27:
                    self.fan.value(1)
                else:
                    self.fan.value(0)
                self.write(font=f10, txt=day, x=5, y=5)
                self.write(font=f10, txt=date, x=42, y=26)
                self.write(font=f10, txt=strftime('%H:%M', localtime()), x=52, y=45)
                self.write(font=f40, txt=str(temp), x=2, y=23)
                self.write(font=f20, txt=str(humid), x=40, y=91)
                sleep(30)
                self.sec_clear(30, 10, 45, 52)  # Date clean-up
                self.sec_clear(75, 35, 23, 2)  # Temperature clean-up
                self.sec_clear(23, 20, 91, 40)  # Humidity clean-up
            except KeyboardInterrupt:
                self.scr_clear()
                self.outline()
                self.write(txt='Aborted!')
                self.i2c.deinit()
                print('aborted!')
                break

            except Exception as e:
                self.scr_clear()
                self.outline()
                self.i2c.deinit()
                print(e)
                break

