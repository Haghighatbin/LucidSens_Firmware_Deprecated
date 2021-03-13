from time import sleep
from machine import Pin, PWM


class DRV8825:
    """ESP32 Micropython class for DRV8825 stepper-motor driver.
    Note: I used this class in a biochemical incubator and sampler...could be modified for other purposes.

    Example:
    from drv8825_esp32 import DRV8825
    drvr = DRV8825(33, 32, 25, 26, 27) # define the gpio pins (DIR, STP, M0, M1, M2)

    drvr.sampling_mode('Full', 0, 1, 3, 5) # (Resolution, direction, cylces, samples, duration)
    # Rotates clockwise with 'Full' resolution for 1 cycle in 3 sampling stations and stops for 5 seconds on each.
    # Resolutions: 'Full', 'Half', '1/4', '1/8', '1/16, '1/32'
     Mode : (m0, m1, m2)
    'Full':  (0, 0, 0)
    'Half':  (1, 0, 0)
    '1/4' :  (0, 1, 0)
    '1/8' :  (1, 1, 0)
    '1/16':  (0, 0, 1)
    '1/32':  (1, 0, 1)
    # Direction: 0 = clockwise ---- 1 = counter-clockwise

    drvr.incubation_mode('Full', 5, 1)
    # Rotates with 'Full' resolution for 5 minutes counter-clockwise

    drvr.interrupter()
    # If an opto-interrupter switch is used, the motor rotates until the switch is interrupted.
    A pin needs to be defined in initialization.
    """

    def __init__(self, dir_pin, step_pin, m0=None, m1=None, m2=None, intrptr=None):
        """Initialization of the stepper driver."""

        self.dir = Pin(dir_pin, Pin.OUT)  # Direction pin
        self.step_pin = step_pin  # Step pin
        if all(_ is not None for _ in [m0, m1, m2]):
            self.m0 = Pin(m0, Pin.OUT)  # Resolution mode pin 0
            self.m1 = Pin(m1, Pin.OUT)  # Resolution mode pin 1
            self.m2 = Pin(m2, Pin.OUT)  # Resolution mode pin 2
        else:
            self.step_mode = 'Full'  # All the resolution pins were considered to be grounded.

        if intrptr is not None:
            self.intrptr = Pin(intrptr, Pin.IN, Pin.PULL_DOWN)

        self.spr = 200  # 200 Steps per revolution: 360 / 1.8
        self.delay = 0.01  # Delay between steps

    def step_resolution(self, step_mode):
        """Defining the resolution of the steps."""

        if self.step_mode == 'Half':
            self.spr = self.spr * 2
            self.delay = self.delay / 2
        elif self.step_mode == '1/4':
            self.spr = self.spr * 4
            self.delay = self.delay / 4
        elif self.step_mode == '1/8':
            self.spr = self.spr * 8
            self.delay = self.delay / 8
        elif self.step_mode == '1/16':
            self.spr = self.spr * 16
            self.delay = self.delay / 16
        elif self.step_mode == '1/32':
            self.spr = self.spr * 32
            self.delay = self.delay / 32
        else:
            pass

        mod_pins = (self.m0, self.m1, self.m2)
        microstep_mode = {'Full': (0, 0, 0),
                          'Half': (1, 0, 0),
                          '1/4': (0, 1, 0),
                          '1/8': (1, 1, 0),
                          '1/16': (0, 0, 1),
                          '1/32': (1, 0, 1)}
        return [i.value(microstep_mode[step_mode][idx]) for idx, i in enumerate(mod_pins)]

    def sampling_mode(self, resolution='Full', direction=0, revolutions=1, samples=3, delay=1):
        """Motor rotates for [revs]cycles;
        in each cycle rotates for 200/[samples];
        stops for [delay]seconds on each sample."""
        stepper = Pin(self.step_pin, Pin.OUT)
        if resolution != 'Full':
            self.step_resolution(resolution)
        self.dir.value(direction if direction in [0, 1] else 0)

        for _ in range(revolutions):
            for _ in range(samples):
                for _ in range(int(self.spr/samples)):
                    stepper.value(1)
                    sleep(self.delay)
                    stepper.value(0)
                    sleep(self.delay)
                sleep(delay)

    def incubation_mode(self, freq=1024, duty=50, duration=1, direction=0):
        """Motor rotates for [duration]minutes."""
        stepper = PWM(Pin(self.step_pin))
        self.dir.value(direction if direction in [0, 1] else 0)
        stepper.duty(duty)

        def ramp_gen(freq):
            _a, _b = 1, 11
            return [int(freq * 1/(1+2**(_a*(x-_b))) * 1/(1+2**(-_a*(x+_b)))) + 10 for x in range(-16, 17)]

        ramp = ramp_gen(freq)
        for frequency in ramp:
            stepper.freq(frequency)
            sleep(round((duration * 60 / sum(ramp)) * frequency, 3))
        stepper.deinit()

    def interrupter(self):
        """An opto-interrupter switch (e.g. ITR9707) could be used to stop the motor at an exact position."""
        self.dir.value(0)
        stepper = Pin(self.step_pin, Pin.OUT)
        if not self.intrptr.value():
            return
        while True:
            stepper.value(1)
            sleep(0.02)
            stepper.value(0)
            if not self.intrptr.value():
                break
        return
