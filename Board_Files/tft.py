from machine import RTC, Pin, DHT
from time import strftime, sleep, localtime
from adc import Sampler
import display
import _thread


class ScrST7735:
    def __init__(self):
        self.tft = display.TFT()
        self.tft.init(self.tft.ST7735R, speed=10000000, spihost=self.tft.VSPI, mosi=23, miso=19, clk=18, cs=5, dc=15,
                      rst_pin=14, hastouch=False, bgr=False, width=128, height=128)

        self.max_x, self.max_y = self.tft.screensize()
        self.init_x, self.init_y = 2, 3
        print('screen size: {}x{} pixel'.format(self.max_x, self.max_y))
        self.rtc = RTC()
        self.adc = Sampler(36)
        self.dht = DHT(Pin(27), DHT.DHT2X)
        self.fan = Pin(12, Pin.OUT)
        self.tft.image(self.init_x + 100, self.init_y + 77, 'ICONS/humidity.jpg', 2, self.tft.JPG)
        self.rtc.ntp_sync(server='cn.pool.ntp.org', tz='CST-8')

    def ntp(self):
        if not self.rtc.synced():
            print('NTP not synced, re-syncing...')
            self.rtc.ntp_sync(server='cn.pool.ntp.org', tz='CST-8')
            sleep(2)

    def welcome(self, signal):
        if signal:
            self.tft.image(self.init_x + 6, self.init_y + 32, 'welcome.jpg', 2)
            sleep(3)
        else:
            self.clear_panel(self.init_x + 2, self.init_y + 21, 120, 110)

    def frame(self):
        self.tft.rect(self.init_x, self.init_y, self.max_x, self.max_y, color=self.tft.BLUE)

    def write(self, font, txt, color, x=2, y=3):
        self.tft.font(font)
        self.tft.text(x, y, txt, color)

    def clear(self):
        self.tft.clear(color=self.tft.BLACK)

    def clear_panel(self, a, b, i, j):
        self.tft.rect(self.init_x + a, self.init_y + b, i, j, color=self.tft.BLACK, fillcolor=self.tft.BLACK)

    def time_panel(self):
        self.clear_panel(self.init_x + 45, self.init_y + 109, 35, 12)  # time panel
        self.write('FONTS/font10B.fon', txt=strftime('%H:%M', localtime()), color=self.tft.GREEN, x=self.init_x + 50,
                   y=self.init_y + 114)

    def date_panel(self):
        self.clear_panel(self.init_x + 26, self.init_y + 96, 72, 12)  # date panel
        # day = strftime('%a', localtime())
        # self.write(font=self.tft.FONT_Default, txt=day, x=5, y=5)
        date = strftime('%d-%b-%Y', localtime())
        self.write('FONTS/font10B.fon', txt=date, color=self.tft.GREEN, x=self.init_x + 32, y=self.init_y + 100)

    def ambient_sensor(self):
        self.clear_panel(self.init_x + 103, self.init_y + 65, 24, 12)  # humidity panel
        self.clear_panel(self.init_x + 5, self.init_y + 24, 93, 40)  # main panel
        sensor = self.dht.read()
        if sensor[0]:
            temperature, humidity = sensor[1], sensor[2]
        else:
            temperature, humidity = '25.1', '55.2'
        self.write('FONTS/font10.fon', txt=str(humidity), color=self.tft.WHITE, x=self.init_x + 103, y=self.init_y + 65)
        self.write('FONTS/font48.fon', txt=str(temperature), color=self.tft.RED, x=self.init_x + 5, y=self.init_y + 37)
        self.write('FONTS/font10.fon', txt='o', color=self.tft.RED, x=self.init_x + 101, y=self.init_y + 37)
        self.write('FONTS/font20B.fon', txt='C', color=self.tft.RED, x=self.init_x + 105, y=self.init_y + 42)

    def hv_panel(self, signal):
        self.clear_panel(self.init_x + 5, self.init_y + 86, 40, 20)
        if signal:
            collected_samples = self.adc.sampler(3, 1, 5)
            voltage = 'HV Output: {:.1f} V'.format(sum(collected_samples)/len(collected_samples))
            self.write('FONTS/font10.fon', txt=voltage, color=self.tft.BLUE, x=self.init_x + 5, y=self.init_y + 86)
            self.adc.deinit()
        else:
            self.clear_panel(self.init_x + 5, self.init_y + 76, 40, 20)

    def serial_status(self, signal):
        self.clear_panel(self.init_x + 104, self.init_y + 3, 22, 22)
        if signal:
            self.tft.image(self.init_x + 104, self.init_y + 3, 'ICONS/serial.jpg', 2, self.tft.JPG)
        else:
            self.tft.image(self.init_x + 104, self.init_y + 3, 'ICONS/noSerial.jpg', 2, self.tft.JPG)

    def wifi_status(self, signal):
        self.clear_panel(self.init_x + 80, self.init_y + 3, 22, 22)
        if signal:
            self.tft.image(self.init_x + 80, self.init_y + 3, 'ICONS/wifi.jpg', 2, self.tft.JPG)
        else:
            self.tft.image(self.init_x + 80, self.init_y + 3, 'ICONS/noWifi.jpg', 2, self.tft.JPG)

    def temp_status(self, signal='idle'):
        self.clear_panel(self.init_x + 56, self.init_y + 3, 22, 22)
        if signal == 'rising':
            self.tft.image(self.init_x + 56, self.init_y + 3, 'ICONS/tempRise.jpg', 2, self.tft.JPG)
        elif signal == 'falling':
            self.tft.image(self.init_x + 56, self.init_y + 3, 'ICONS/tempFall.jpg', 2, self.tft.JPG)
        else:
            self.tft.image(self.init_x + 56, self.init_y + 3, 'ICONS/temp.jpg', 2, self.tft.JPG)

    def opr_status(self, signal):
        self.clear_panel(self.init_x + 32, self.init_y + 3, 22, 22)
        if signal == 'hv':
            self.tft.image(self.init_x + 32, self.init_y + 3, 'ICONS/hv.jpg', 2, self.tft.JPG)
        elif signal == 'stepper':
            self.tft.image(self.init_x + 32, self.init_y + 3, 'ICONS/stepper.jpg', 2, self.tft.JPG)
        elif signal == 'detector':
            self.tft.image(self.init_x + 32, self.init_y + 3, 'ICONS/phDetector.jpg', 2, self.tft.JPG)
        elif signal == 'done':
            self.tft.rect(self.init_x + 32, self.init_y + 3, 22, 22, color=self.tft.BLACK, fillcolor=self.tft.BLACK)
        else:
            pass

    def connect_status(self):
        self.clear_panel(self.init_x + 8, self.init_y + 3, 22, 22)
        self.tft.image(self.init_x + 8, self.init_y + 3, 'ICONS/connect.jpg', 2, self.tft.JPG)

    def wait_status(self, signal):
        if signal:
            self.clear_panel(self.init_x + 47, self.init_y + 112, 35, 12)  # time panel
            self.clear_panel(self.init_x + 28, self.init_y + 99, 72, 12)  # date panel
            self.clear_panel(self.init_x + 7, self.init_y + 27, 93, 65)  # main panel
            self.tft.image(self.init_x + 7, self.init_y + 27, 'ICONS/wait.jpg', 0, self.tft.JPG)

    def tft_close(self):
        self.clear()
        self.frame()
        self.write(font='FONTS/font20B.fon', txt='deinitialized!', color=self.TFT.RED, x=20, y=60)
        self.tft.deinit()
        print('TFT module deinitialized.')

    def status_thrd(self):
        self.tft.image(self.init_x + 100, self.init_y + 77, 'ICONS/humidity.jpg', 2, self.tft.JPG)
        _thread.allowsuspend(True)
        while True:
            ntf = _thread.getnotification()
            if ntf == _thread.EXIT:
                print('STATUS thread received EXIT command.')
                return
            try:
                self.ntp()
                self.ambient_sensor()
                self.date_panel()
                self.time_panel()
                sleep(10)
            except KeyboardInterrupt:
                print('Display aborted.')
                break
            except Exception as e:
                print('exception received!')
                print(e)
                break
