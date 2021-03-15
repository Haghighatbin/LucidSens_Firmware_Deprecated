from machine import Pin, ADC, PWM, RTC, DHT, stdin_get, stdout_put
p14 = Pin(14, Pin.OUT, value=0)
p15 = Pin(15, Pin.OUT, value=0)
p5 = Pin(5, Pin.OUT, value=0)
print('Pins 4, 14, 15 are all down now.')
import network, sys, gc, _thread
from display import TFT
_thread.stack_size(3*4096)
print('THREAD stack_size is: {}'.format(_thread.stack_size()))
from utime import ticks_ms, ticks_diff, sleep_ms, sleep, strftime, localtime
import usocket as socket
from upysh import *
import ujson as json
from array import array

# color codes
green = '\033[92m'
red = '\033[91m'
cyan = '\033[96m'
pink = '\033[95m'
yellow = '\033[93m'
white = '\033[97m'

class testAsteroid:
    def test_asteroid(self, iterations):
        n = iterations
        response = ({'header': 'test_asteroid'})
        response.update({'body': [[(i, 0), (0, abs(abs(i) - n)), (0, -(abs(abs(i) - n)))] for i in range(-n, n + 1)]})
        jsnd_response = json.dumps(response)
        return jsnd_response

class adcSampler:
    def __init__(self, pin):
        self.adc = ADC(pin)
        if pin == 36:
            self.mode = 'hv'
            # print('ADC is now sampling in {} mode.'.format(self.mode.upper()))
        elif pin in [34, 39]:
            self.mode = 'sipm'
            # print('ADC is now sampling in {} mode.'.format(self.mode.upper()))
        else:
            raise RuntimeError('Invalid pin definition or wrong call.')
        self.adc.atten(ADC.ATTN_11DB)

    def sampler(self, acquisition=3, intervals=0.1, raw_to_avrg=10):
        """
        :param acquisition: ADC total reading time in seconds
        :param intervals: sampling intervals in seconds
        :param raw_to_avrg: number of raw samples to be picked and averaged between two intervals
        returns an array[list] of ADC reads
        """
        def calibration(data):
            if self.mode == 'hv':
                return (data + 95.68)/78.14
            elif self.mode == 'sipm':
                return (data + 183.7)/1276.1
            else:
                raise RuntimeError('Invalid pin definition or wrong call.')
        frq = int(raw_to_avrg / intervals)
        datapoint = array('H', raw_to_avrg)
        true_set = array('d')
        calib_set = array('d')
        start_tot = ticks_ms()
        for _ in range(int(acquisition/intervals)):
            self.adc.collect(freq=frq, data=datapoint)
            start = ticks_ms()
            while True:
                try:
                    if not self.adc.progress()[0]:
                        end = ticks_ms()
                        true_val = self.adc.collected()[2]
                        calib_val = calibration(self.adc.collected()[2])
                        # print('{} ms took to collect one averaged data-point.'.format(ticks_diff(end, start)))
                        true_set.append(true_val)
                        calib_set.append(calib_val)
                        break
                    else:
                        pass
                except KeyboardInterrupt:
                    # print('aborted.')
                    self.adc.deinit()
                    break
                except Exception as e:
                    self.adc.deinit()
                    print(e)
                    break
        end_tot = ticks_ms()
        # print('{} ms took to collect the true_set.'.format(ticks_diff(end_tot, start_tot)))
        # print('true val: {}'.format(sum(true_set)/len(true_set)))
        # print('calib val: {}'.format(sum(calib_set)/len(calib_set)))

        return calib_set

    def deinit(self):
        self.adc.deinit()
        # return 'ADC module deinitialized.'

class commandHandler:
    def __init__(self):
        self.clear = clear
        self.seg_size = 510

    def read_until(self, ending, timeout=10000):
        try:
            self.read = stdin_get(1, timeout)
            if self.read is None:
                self.read = ''
            else:
                pass
            timeout_count = 0
            while True:
                if self.read is not None:
                    if self.read.endswith(ending):
                        break
                    else:
                        new_data = stdin_get(1, timeout)
                        self.read += new_data
                        timeout_count = 0
                elif self.read is None:
                    # print('read is None')
                    break
                else:
                    timeout_count += 1
                    if timeout is not None and timeout_count >= timeout:
                        break
        except KeyboardInterrupt:
            # print('aborted.')
            sys.exit(0)
        except:
            pass
        return self.read

    def sender(self, response):
        def chunker(cmd):
            # return [cmd[i:i + self.pck_size] for i in range(0, len(cmd), self.pck_size)]
            data = []
            segments = [cmd[i:i + self.seg_size] for i in range(0, len(cmd), self.seg_size)]
            for segment in segments:
                if segment == segments[-1]:
                    data.append(segment + '*#')
                else:
                    data.append(segment + '_#')
            return data
        self.clear
        try:
            if len(response) > self.seg_size:
                # for idx, data in enumerate([chunk for chunk in chunker(response)]):
                for data in ([chunk for chunk in chunker(response)]):
                    self.machine.stdout_put(data)
                    sleep(1)
                    resp = self.read_until('#', 5000)
                    if 'EOF received.\n' in resp:
                        pass
                    elif 'got it!\n' in resp:
                        pass
                    else:
                        while True:
                            self.machine.stdout_put(data)
                            sleep(1)
                            resp = self.read_until('#', 5000)
                            if 'EOF received.\n' in resp:
                                break
                            elif 'got it!\n' in resp:
                                break
                            else:
                                sleep(2)
                                pass
            else:
                self.machine.stdout_put(response)
                sleep(2)
                resp = self.read_until('#', 5000)
                if 'EOF received.\n' in resp:
                    pass
                elif 'got it!\n' in resp:
                    pass
                else:
                    while True:
                        self.machine.stdout_put(response)
                        sleep(1)
                        resp = self.read_until('#', 5000)
                        if 'got it!' in resp:
                            break
                        elif 'EOF received.\n' in resp:
                            break
                        else:
                            sleep(2)
                            pass
            sleep(1)

        except KeyboardInterrupt:
            print('Aborted!')
        except Exception as e:
            print(e)

    def operator_func(self, command):
        if command['header'] == 'test':
            import test_A
            asteroid = test_A.TestAsteroid()
            resp = open('resp.txt', 'w')
            resp.write(asteroid.test_asteroid(command['body']['it']))
            resp.close()
            r = open('resp.txt', 'r')
            for line in r:
                self.sender(line)
            return

        # if command['header'] == 'run':
        #     if command['body']['it'] is not None:
        #         from drv8825_esp32_gpio import DRV8825
        #         drvr = DRV8825(33, 32, 25, 26, 27)
        #         response = ({'header': 'run_incubator'}, {'body': 'incubation initialized.'})
        #         print(json.dumps(response))
        #         drvr.incubation_mode('Full', command['body']['it'], 0)
        #         return

    def __str__(self):
        print("Operator class is activated.")

class stprDRV8825:
    """ESP32 (PWM-based) Micropython class for DRV8825 stepper-motor driver.

    Example:
    from drv8825 import DRV8825
    drvr = DRV8825(13, 33, 32, 35) # define your gpio pins (PWR, DIR, STP, INTRPTR)

    # Resolutions: predefined as 'Full' (pins were grounded)
    # Direction: 0 = clockwise ---- 1 = counter-clockwise

    incubation_mode([freq=1024], [duty=50], [duration=1], [direction=0])
    drvr.incubation_mode(1024, 50, 5, 1)
    Rotates with 'Full' resolution for 5 minutes counter-clockwise
    pwm freq: 1024 Hz (100 - 3600 Hz) ---- duty-cycle: 50 (0 - 100) (%)

    sampling_mode(self, direction=0, cycles=1, samples=3, acquisition_time=5)
    drvr.sampling_mode(0, 1, 3, 20)
    Rotates [clockwise] for [3]; in each cycle rotates for 200/[3] * 1.8 degrees;
    stops for [5]seconds on each sample.

    """
    def __init__(self, pwr_pin, dir_pin, step_pin, intrptr_pin):
        """Initialization of the stepper driver."""
        self.pwr = Pin(pwr_pin, Pin.OUT)
        self.dir = Pin(dir_pin, Pin.OUT)
        self.intrptr = Pin(intrptr_pin, Pin.IN)
        self.step_pin = step_pin
        self.spr = 200  # 200 Steps per revolution: 360 / 1.8
        self.delay = 0.01  # Delay between steps
        self.dir.value(0)

    def incubation_mode(self, freq=1024, duty=50, duration=1, direction=0):
        """Motor rotates for [duration]minutes."""
        stepper = PWM(self.step_pin)
        try:
            self.dir.value(direction if direction in [0, 1] else 0)
            stepper.duty(duty)

            def ramp_gen(freq):
                _a, _b = 1, 11
                return [int(freq * 1/(1+2**(_a*(x-_b))) * 1/(1+2**(-_a*(x+_b)))) + 10 for x in range(-16, 17)]

            ramp = ramp_gen(freq)
            self.pwr.value(1)
            for frequency in ramp:
                stepper.freq(frequency)
                sleep(round((duration * 60 / sum(ramp)) * frequency, 3))
            sleep(3)
            stepper.deinit()
        except KeyboardInterrupt:
            print('Aborted!')
            stepper.deinit()
            self.interrupter()
        except Exception as e:
            stepper.deinit()
            self.interrupter()
            print(e)
        finally:
            stepper.deinit()
            self.interrupter()

    def sampling_mode(self, direction=0, cycles=1, samples=3, acquisition_time=1):
        """Motor rotates clockwise for [revs]cycles;
        in each cycle rotates for 200/[samples] * 1.8 degrees;
        stops for [acquisition_time]seconds on each sample."""
        stepper = Pin(self.step_pin, Pin.OUT)
        self.pwr.value(1)
        try:
            self.dir.value(direction if direction in [0, 1] else 0)
            for _ in range(cycles):
                for _ in range(samples):
                    for _ in range(int(self.spr/samples)):
                        stepper.value(1)
                        sleep(self.delay)
                        stepper.value(0)
                        sleep(self.delay)
                    sleep(acquisition_time)
            sleep(3)
        except KeyboardInterrupt:
            print('Aborted!')
            self.interrupter()
        except Exception as e:
            print(e)
            self.interrupter()
        finally:
            stepper.value(0)
            self.interrupter()

    def interrupter(self):
        """Motor rotates clockwise to finally be stopped by the opto-interrupter."""
        self.dir.value(0)
        self.pwr.value(1)
        stepper = Pin(self.step_pin, Pin.OUT)
        if not self.intrptr.value():
            self.pwr.value(0)
            return
        while True:
            stepper.value(1)
            sleep(0.02)
            stepper.value(0)
            if not self.intrptr.value():
                self.pwr.value(0)
                break
        return

class scrST7735:
    def __init__(self):
        self.tft = TFT()
        self.tft.init(self.tft.ST7735R, speed=10000000, spihost=self.tft.VSPI, mosi=23, miso=19, clk=18, cs=5, dc=15,
                      rst_pin=14, hastouch=False, bgr=False, width=128, height=128)

        self.max_x, self.max_y = self.tft.screensize()
        self.init_x, self.init_y = 2, 3
        print('screen size: {}x{} pixel'.format(self.max_x, self.max_y))
        self.rtc = RTC()
        self.adc = adcSampler(36)
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
           
class serialConnection:
    def __init__(self):
        self.read = ''
        self.signal = ''
        self.content = ''
        self.opr = commandHandler()
        self.clear = clear

    def read_until(self, ending, timeout=10000):
        try:
            self.read = stdin_get(1, timeout)
            if self.read is None:
                self.read = ''
            else:
                pass
            timeout_count = 0
            while True:
                if self.read is not None:
                    if self.read.endswith(ending):
                        break
                    else:
                        new_data = stdin_get(1, timeout)
                        self.read += new_data
                        timeout_count = 0
                elif self.read is None:
                    # print('read is None')
                    break
                else:
                    timeout_count += 1
                    if timeout is not None and timeout_count >= timeout:
                        break
        except:
            pass
        return self.read

    def sr_handler(self, cmd):
        self.opr.operator_func(cmd)
        return

    def sr_receiver(self):
        self.clear
        while True:
            try:
                # print('sr_thread: sending READY signal.')
                # machine.stdout_put('s_thread: READY.\n')
                # utime.sleep(1)
                # while 'go#' not in self.read_until('#'):
                while 'go#' not in self.signal and '!#' not in self.signal:
                    stdout_put('s_thread: READY.\n')
                    sleep(2)
                    self.signal = self.read_until('#')

                if '!#' in self.signal:
                    print('aborted by user.')
                    break
                else:
                    stdout_put('got it!\n')
                    self.clear

                while '*' not in self.content:
                    try:
                        data = self.read_until('#')
                        # print(data)
                        if '#' in data and data[:-2] not in self.content:
                            if data[-2] == '*':
                                self.content += data[:-1]
                                break
                            elif data[-2] == '_':
                                self.content += data[:-2]
                                stdout_put('got it!\n')
                            else:
                                sleep(1)
                                pass
                        else:
                            pass
                    except:
                        break
                sleep(1)
                if '*' in self.content:
                    stdout_put('EOF received.\n')
                    # print('Content: {}\n'.format(content))
                    # print('length: {} chars\n'.format(len(content)))
                    print('saving cmd file\n')
                    raw_cmd = open('cmd.txt', 'w')
                    raw_cmd.write(self.content[:-1])
                    raw_cmd.close()
                    resp = open('cmd.txt', 'r')
                    print('evaling cmd in resp.\n')
                    for line in resp:
                        cmd = eval(line)
                        self.sr_handler(cmd)
                    resp.close()
                    print('closed resp.\n')
            except KeyboardInterrupt:
                print('Keyboard interrupt')
                sys.exit(0)
            except Exception as e:
                print(e)
                break

    def __str__(self):
        return "Serial connection is established."

class wifiConnection:
    """
    ip = '192.168.0.95'
    port = 3175
    subnet = '255.255.255.0'
    gateway = '192.168.1.1'
    dns = '208.67.222.222'
    essid = 'TP-LINK_CFF1'
    password = 'ecl534534'
    essid = 'tplink'
    password = 'Amin_3175!?$'
    """
    def __init__(self):
        self.p_led = Pin(2, Pin.OUT)
        self.clear = clear
        try:
            f = open("account.txt", 'r')
            for lines in f:
                for line in lines.split('\r'):
                    if "#" in line:
                        pass
                    elif "ip" in line:
                        self.ip = line.split(' ')[2]
                    elif "port" in line:
                        self.port = int(line.split(' ')[2])
                    elif "subnet" in line:
                        self.subnet = line.split(' ')[2]
                    elif "gateway" in line:
                        self.gateway = line.split(' ')[2]
                    elif "dns" in line:
                        self.dns = line.split(' ')[2]
                    elif "essid" in line:
                        self.essid = line.split(' ')[2]
                    elif "password" in line:
                        self.password = line.split(' ')[2]
                    else:
                        # print("\nw_thread: something wrong with the account file...")
                        pass
            print("\nw_thread: done getting wifi credentials...")
            f.close()

        except Exception as e:
            print("\nw_thread: something wrong with the account file...\n")
            print(e)
            pass

    def wf_handler(self):
        opr = commandHandler()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.ip, self.port))
        while True:
            try:
                self.clear
                print('\nw_thread: READY.')
                sock.listen(5)
                conn, addr = sock.accept()
                while True:
                    try:
                        if conn:
                            print("w_thread: received a call from: {}".format(addr))
                            print("w_thread: sending command to operator...")
                            cmd = conn.recv(4096).decode()
                            parsed_cmd = json.loads(cmd)
                            if parsed_cmd['header'] in ['run', 'tst']:
                                conn.sendall(opr.operator_func(parsed_cmd))
                                print('w_thread: response is sent.')
                                break
                                # sock.close()
                            else:
                                # sock.close()
                                break
                        else:
                            print("w_thread: something went run with the connection!")
                            # sock.close()
                            break
                    except KeyboardInterrupt:
                        print("\nw_thread: aborted by user!")
                        break
                    except Exception as e:
                        print(e)
                        break

            except KeyboardInterrupt:
                print("\nw_thread: aborted by user!")
                sock.close()
                break

            except Exception as e:
                print(e)
                print("w_thread: closing socket in try_receiver.")
                sock.close()
                break

    def wf_connection(self):
        counts = 0
        station = network.WLAN(network.STA_IF)
        try:
            if station.isconnected():
                print(station.ifconfig())
                print("w_thread: wifi is already connected.")
                self.p_led.value(1)
                return station.isconnected()

            else:
                station.active(True)
                print("w_thread: wifi has not been connected yet.")
                sleep(3)
                print("w_thread: scanning network...")

                scanned = station.scan()
                modified_scanned_list = [list(j for idx, j in enumerate(signal) if idx not in [1, 4, 6]) for signal in scanned]
                header = ['ESSID', 'Channel', 'RSSI', 'AuthMode']
                row_format = "|{:^30}|" * (len(header))
                print(128 * '-')
                print(row_format.format(*header))
                print(128 * '-')
                print('\n'.join(row_format.format(*row) for row in modified_scanned_list))
                print(128 * '-', '\n')

                print("w_thread: connecting to the pre-defined:\nessid: {}\npassword: {}\n".format(self.essid, self.password))
                station.connect(self.essid, self.password)
                sleep(3)

            if station.isconnected():
                # print("Connection established.")
                station.config('mac')
                # print("executing ifconfig command")
                station.status()
                # print("setting up the static IP")
                station.ifconfig((self.ip, self.subnet, self.gateway, self.dns))
                # print("re-executing ifconfig command:")
                print(station.ifconfig())
                self.p_led.value(1)
            return station.isconnected()

        except Exception as e:
            print(e)
            return station.isconnected()

    def wf_disconnect(self):
        station = network.WLAN(network.STA_IF)
        station.disconnect()
        print("w_thread: wifi is not connected.")
        station.active(False)
        self.p_led.value(0)
        return

    def auth_mode(self, mod):
        lst = {0: 'open',
               1: 'WEP',
               2: 'WPA-PSK',
               3: 'WPA2-PSK',
               4: 'WPA/WPA2-PSK'
               }
        return lst.get(mod)

    def hidden(self, mod):
        lst = {False: "visible",
               True: "hidden"}
        return lst.get(mod)

    def __str__(self):
        print("WiFiConn class is activated.")

def main():
    # gc.enable()
    def gc_thrd():
        _thread.allowsuspend(True)
        while True:
            ntf = _thread.getnotification()
            if ntf == _thread.EXIT:
                print('GC thread received EXIT command.')
                return
            gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
            if gc.mem_free() < gc.threshold():
                gc.collect()
                print('available memory now: {}'.format(gc.mem_free()))
            sleep(10)
    try:
        tft = scrST7735()
        tft.clear()
        tft.welcome(True)
        tft.connect_status()
        tft.serial_status(False)
        tft.temp_status()
        tft.welcome(False)
        tft.frame()

        print('establishing wifi connection.')
        wf = wifiConnection()
        if wf.wf_connection():
            tft.wifi_status(True)
            print(yellow + "WIFI is connected." + green)
            # wf_thrd = _thread.start_new_thread('wifi_thread', wf.wf_handler, ())
        else:
            wf.wf_disconnect()
            print(red + 'wifi is not connected.' + green)
            tft.wifi_status(False)

        tft.hv_panel(True)

        print('initializing the stepper.')
        tft.opr_status('stepper')
        stpr = stprDRV8825(13, 33, 32, 35)
        stpr.interrupter()
        print(red + 'stepper adjusted to zero-point.' + green)
        tft.opr_status('done')

        # print('activated threads:\n')
        # print('\n'.join(pink + str(thrd) + green for thrd in _thread.list(False)))

        print('establishing serial connection.')
        sr = serialConnection()
        tft.serial_status(True)

        gc_thrd = _thread.start_new_thread('gc_thrd', gc_thrd, ())
        print(cyan + 'GC thread is activated.' + green)
        sleep(1)
        status_thrd = _thread.start_new_thread('status_thrd', tft.status_thrd, ())
        sleep(1)
        print(cyan + 'STATUS thread activated.' + green)
        sleep(1)
        print(cyan + 'SERIAL thread is activated.' + green)
        serial_thrd = _thread.start_new_thread('serial_thrd', sr.sr_receiver, ())

    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(e)
        print(red + 'main module interrupted.' + green)


if __name__ == '__main__':
    main()
