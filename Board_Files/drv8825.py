from time import sleep
from machine import Pin, PWM


class DRV8825:
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

