from machine import RTC, Pin, I2C
from ssd1306 import SSD1306_I2C, const
import f10, f20, f40
from Board_Files.writer import Writer
from utime import strftime, sleep, localtime


class Oled:
    def __init__(self, scl_pin=22, sda_pin=21):
        self.WIDTH = const(128)
        self.HEIGHT = const(64)
        self.MARGIN = 1
        self.SFont = f10
        self.MFont = f20
        self.LFont = f40
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

    def frame(self):
        for i in range(self.MARGIN, self.WIDTH - self.MARGIN):
            self.oled.pixel(i, self.MARGIN, 1)
            self.oled.pixel(i, self.HEIGHT - self.MARGIN, 1)
        for i in range(self.MARGIN, self.HEIGHT - self.MARGIN):
            self.oled.pixel(self.WIDTH - self.MARGIN, i, 1)
            self.oled.pixel(self.MARGIN, i, 1)
        self.oled.show()

    def ntp(self):
        rtc = RTC()
        print('Syncing NTP...')
        rtc.ntp_sync(server='cn.pool.ntp.org', tz='CST-8')
        if not rtc.synced:
            print('RTC not synced, give it a bit of time...')
            sleep(2)
            if rtc.synced:
                print('RTC now synced.')
            else:
                print('RTC have not synced, pass.')
        sleep(1)

    def now_time_thrd(self):
        self.write(font=f20, txt='C', x=4, y=78)
        self.write(font=f10, txt='o', x=2, y=73)
        self.oled.show()
        while True:
            try:
                self.write(font=f10, txt=strftime('%H:%M', localtime()), x=50, y=45)
                sleep(61)
                self.sec_clear(30, 10, 45, 50)
            except Exception as e:
                print(e)
                break

    def now_temp_thrd(self):
        while True:
            try:
                self.write(font=f10, txt='27', x=2, y=25)
                sleep(61)
                self.sec_clear(45, 35, 25, 2)
            except Exception as e:
                print(e)
                break

    def now_humid_thrd(self):
        self.write(font=f10, txt='%', x=50, y=118)
        self.hum_icon(x=38, y=118)
        self.oled.show()
        while True:
            try:
                self.write(font=f10, txt='55', x=40, y=93)
                sleep(61)
                self.sec_clear(23, 20, 93, 40)
            except Exception as e:
                print(e)
                break

    def routine(self):
        self.scr_clear()
        self.ntp()
        self.frame()
        day = strftime('%a', localtime())
        date = strftime('%d-%b-%Y', localtime())
        self.write(font=self.SFont, txt=day, x=5, y=5)
        self.write(font=self.SFont, txt=date, x=38, y=29)

