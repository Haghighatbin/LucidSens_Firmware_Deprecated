from time import sleep
from machine import Pin, PWM


class DRV8825:
    """ESP32 (PWM-based) Python3 class for DRV8825 stepper-motor driver.

    Example:
    from drv8825_esp32_pwm import DRV8825
    drvr = DRV8825(33, 32, 25, 26, 27) # define the gpio pins (DIR, STP, M0, M1, M2)

    # Resolutions: 'Full', 'Half', '1/4', '1/8', '1/16, '1/32'
    # Direction: 0 = clockwise ---- 1 = counter-clockwise
    
    # Rotates with 'Full' resolution for 5 minutes counter-clockwise
    # pwm freq: 500Hz (1 - 1kHz) ---- duty-cycle: 512 for 50% (0 - 1023)
    drvr.incubation_mode('Full', 500, 512, 5, 1)
    
    """

    def __init__(self, dir_pin, step_pin, m0_pin, m1_pin, m2_pin):
        """Initialization of the stepper driver."""

        self.dir = Pin(dir_pin, Pin.OUT)  # Direction pin
        self.step = PWM(step_pin)  # Step pin

        self.m0 = Pin(m0_pin, Pin.OUT)  # Resolution mode pin 0
        self.m1 = Pin(m1_pin, Pin.OUT)  # Resolution mode pin 1
        self.m2 = Pin(m2_pin, Pin.OUT)  # Resolution mode pin 2
        [_.off() for _ in [self.dir, self.m0, self.m1, self.m2]]  # Grounding all pins

    def step_resolution(self, step_mode):
        """Defining the resolution of the steps."""

        mod_pins = (self.m0, self.m1, self.m2)
        microstep_mode = {'Full': (0, 0, 0),
                          'Half': (1, 0, 0),
                          '1/4': (0, 1, 0),
                          '1/8': (1, 1, 0),
                          '1/16': (0, 0, 1),
                          '1/32': (1, 0, 1)}
        return [i.value(microstep_mode[step_mode][idx]) for idx, i in enumerate(mod_pins)]

    def incubation_mode(self, resolution='Full', freq=1023, duty=512, duration=1, direction=0):
        """Motor rotates for [duration]minutes."""
        self.step_resolution(resolution)
        try:
            self.dir.value(direction if direction in [0, 1] else 0)
            self.step.duty(duty)

            # _a and _b are defining the structure of the frequency ramp profile, width and steepness.
            def ramp_gen(freq):
                _a, _b = 3, 6
                return [int(freq * 1 / (1 + 2 ** (_a * (x - _b))) * 1 / (1 + 2 ** (-_a * (x + _b)))) for x in range(-10, 11)]
            ramp = ramp_gen(freq)
            for frequency in ramp:
                self.step.freq(frequency)
                sleep(round((duration * 60 / sum(ramp)) * frequency, 2))
        except KeyboardInterrupt:
            print('Aborted!')
        except Exception as e:
            print(e)
        finally:
            self.step.duty(0)
            [_.off() for _ in [self.dir, self.m0, self.m1, self.m2]]

