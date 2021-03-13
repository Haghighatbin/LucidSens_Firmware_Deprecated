"""Raspberry Pi Python module for DRV8825 driver coupled with a NEMA 17 stepper motor."""
from time import sleep
import RPi.GPIO as gpio

gpio.setmode(gpio.BCM)


class DRV8825:
    """Class for DRV8825 stepper motor driver."""

    def __init__(self, dir_pin, step_pin, m0_pin, m1_pin, m2_pin):
        """Initialization of the stepper driver."""

        self.dir = dir_pin  # Direction pin
        self.step = step_pin  # Step pin

        gpio.setup(self.dir, gpio.OUT)
        gpio.setup(self.step, gpio.OUT)

        self.m0 = m0_pin  # Resolution mode pin 0
        self.m1 = m1_pin  # Resolution mode pin 1
        self.m2 = m2_pin  # Resolution mode pin 2

        self.cw = 0  # Clock-Wise rotation
        self.ccw = 1  # Counter-Clock-Wise rotation
        self.spr = 180  # + 20 = 200 ## Steps per revolution: 360 / 1.8
        self.delay = 0.001 # Delay between steps

    def step_resolution(self, step_mode):
        """Defining the resolution of the steps."""

        mode_pins = (self.m0, self.m1, self.m2)
        gpio.setup(mode_pins, gpio.OUT)
        gpio.output(mode_pins, (0,0,0))
        microstep_mode = {'Full': (0, 0, 0),
                          'Half': (1, 0, 0),
                          '1/4': (0, 1, 0),
                          '1/8': (1, 1, 0),
                          '1/16': (0, 0, 1),
                          '1/32': (1, 0, 1)}
        gpio.output(mode_pins, microstep_mode[step_mode])

    def sampling_mpde(self, resolution='Full', revolutions=1, samples=3, delay=1, direction=0):
        """Motor rotates for [revs]cycles;
        in each cycle rotates for 200/[samples];
        stops for [delay]seconds on each sample."""

        self.step_resolution(resolution)  # Setting up the resolution
        direct = self.cw if not direction else self.ccw  # Direction --> [clock-wise: 0 ---- counter-clock-wise: 1])
        gpio.output(self.dir, direct)

        for _ in range(revolutions):
            # Number of samples
            for _ in range(samples):
            # 180 steps considered to get a whole number for odd number of samples(e.g. 3)
                for _ in range(int(self.spr/samples)):
                    gpio.output(self.step, gpio.HIGH)
                    sleep(self.delay)
                    gpio.output(self.step, gpio.LOW)
                    sleep(self.delay)
                sleep(delay)
            # +20 final steps to return to the initial point
            for _ in range(20):
                gpio.output(self.step, gpio.HIGH)
                sleep(self.delay)
                gpio.output(self.step, gpio.LOW)
                sleep(self.delay)
        gpio.cleanup()

    def incubation_mode(self, duration=3, direction=0):
        """Motor rotates for [duration]minutes."""
        self.step_resolution('Full')
        direct = 0 if not direction else 1
        gpio.output(self.dir, direct)

        for _ in range(int(60 * duration/(200 * self.delay * 2))):
            for _ in range(200):
                gpio.output(self.step, gpio.HIGH)
                sleep(self.delay)
                gpio.output(self.step, gpio.LOW)
                sleep(self.delay)
        gpio.cleanup()


# Example
s = DRV8825(20, 21, 14, 15,18)

# Rotates clock-wise with Full resolution for 1 cycle, # in 3 sampling stations and stops for 5 seconds on each.
#s.sampling_mpde('Full', 1, 3, 5, 0)

# Rotates for 5 minutes clock-wise
s.incubation_mode(5, 1)
