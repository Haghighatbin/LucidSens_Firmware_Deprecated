#!/usr/bin/env python
import spidev
import RPi.GPIO as gpio
import time


class ADS1232:
    """
    A spidev-based Python3 class to read data from the 2-channel 24-bit ADS1232 (Texas Instruments) analog-digital-converter (ADC).
    The chip includes an onboard temperature sensor controllable via TEMP pin as well as onboard selectable programmable
    gain amplifier (PGA) of 1, 2, 64, 128 in a full-scale differential ranges of +/- (2.5, 1.25, 0.039, 0.019 V) controllable
    via GAIN0 and GAIN1 pins. The data could be output at either 10SPS or 80SPS based on the SPEED pin status. The A0 pin
    could be used to select the analog input channel.
    As a quick reference for pin connections:
        DVDD, AVDD, REFP ---> (2.7 - 5.3V)
        DGND, CLKIN, REFN, AGND ---> GND
        XTAL1/XTAL2 ---> External crystal clock: could be both grounded if not using an external crystal
        A0 ---> Input Mux Select: Low for AIN1
                                  High for AIN2
        SPEED ---> Data rate select: Low: 10SPS
                                     High: 80SPS
        GAIN0/GAIN1 ---> Gain select: Low/Low    # gain 1
                                      Low/High   # gain 2
                                      High/Low   # gain 64
                                      High/High  # gain 128
        CAPS ---> Gain amp bypass capacitors: two pins could be bridged together via a 0.1uF ceramic capacitor
        AINP1-2/AINN1-2 ---> Positive/Negative analog input channels: whatever you choose ground the other ones.

        DRDY/DOUT ---> Data-ready/Data-output: could be connected to MISO pin on microcontroller (RPi)
        SCLK ---> Serial clock: could be connected to SCLK pin on microcontroller (RPi)
        PDWN ---> Power-Down: Holding this pin low powers down the entire converter and resets the ADC

    """

    def __init__(self, SPI_BUS=0, SPI_DEV=0, GAIN0=22, GAIN1=23, PWDN=24, TMP=27, SPEED=18, VREF=3.3, A0=None,
                 g_sclk=16, g_miso=20):
        """
        Python Spidev module was used to interface with the ADS1232,
        for more information refer to https://pypi.org/project/spidev/
        As default values <bus> and <device> were set to 0, check /dev/spidev<bus>.<device> if yours are different.

        Default gpio pin and VDD values were set to meet my own interests, please change them to your own desired values
        Note: The analog input range at a gain of 1 or 2 is from GND-100mV to AVDD+100mV, while at a gain of 64 or 128
         the input range is reduced to between GND+1.5V to AVDD-1.5V.
        The measurement range is based on the VREF(REFP-REFN), where the full-scale range(FSR) is +/- 0.5*VREF.
        If AINN and REFN are both grounded, then only half of the FSR will be used.
        Including the gain into the above equation: 0.5 * VREF/gain.
        As an example, considering AINP1 as the input and VREF=3.3V, REFN=AINN1=GND, then:
        for gain 1:     0 - 1.650V
            gain 2:     0 - 0.825V
            gain 64:    0 - 0.025V
            gain 128:   0 - 0.013V
        """
        self.spi_bus = SPI_BUS
        self.spi_dev = SPI_DEV
        self.g0 = GAIN0
        self.g1 = GAIN1
        self.pwdn = PWDN
        self.tmp = TMP
        self.spd = SPEED
        self.vref = VREF  # Considering (REFP=VDD and REFN=GND) and vice versa
        self._sclk = g_sclk
        self._miso = g_miso
        self._mux = A0

        self.spi = spidev.SpiDev()
        self.spi.open(self.spi_bus, self.spi_dev)  # channeling to /dev/spidev<bus>.<device>

        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)

        gpio.setup(self.pwdn, gpio.OUT)
        gpio.setup(self.g0, gpio.OUT)
        gpio.setup(self.g1, gpio.OUT)
        gpio.setup(self.tmp, gpio.OUT)
        gpio.setup(self.spd, gpio.OUT)

        if self._mux is not None:
            gpio.setup(self._mux, gpio.OUT)

        if self._miso is not None:
            gpio.setup(self._miso, gpio.IN, pull_up_down=gpio.PUD_DOWN)

    def standby_mode(self, status):
        if self._miso is None and self._sclk is None:
            raise RuntimeError('No GPIO pins were assigned to monitor the MISO and SCLK pins.')
        else:
            if status:
                if not gpio.input(self._miso):
                    gpio.setup(self._sclk, gpio.OUT)
                    gpio.output(self._sclk, 1)
                else:
                    raise RuntimeError('The DRDY/DOUT pin is in High status, try again when the pin goes Low.')
            elif not status:
                if not gpio.gpio_function(self._sclk):
                    pass
                else:
                    gpio.output(self._sclk, 0)
                    gpio.cleanup(self._sclk)
            else:
                raise ValueError('Use True(1)/False(0) to activate/deactivate the Standby Mode.')

    def offset_calibration(self):
        if self._miso is None:
            raise RuntimeError('No GPIO pin was assigned to monitor the MISO pin.')
        else:
            self.spi.xfer2([0, 0, 0, 0])
            while gpio.input(self._miso):
                pass
            print('Offset calibration is done.')

    def standby_offset_calibration(self, status):
        if self._sclk is None:
            raise RuntimeError('No GPIO pin was assigned to monitor the SCLK pin.')
        elif status:
            self.spi.xfer2([0, 0, 0, 0])
            gpio.setup(self._sclk, gpio.OUT)
            gpio.output(self._sclk, 1)
        elif not status:
            if not gpio.gpio_function(self._sclk):
                    pass
            else:
                gpio.output(self._sclk, 0)
                gpio.cleanup(self._sclk)
        else:
            raise ValueError('Use True(1)/False(0) to activate/deactivate the Standby-Offset-Calibration Mode.')
        
    def chip_power(self, status):
        """
        Pulling down the PWDN pin shuts down the entire ADC circuitry and reduces the  power consumption to almost zero.
        The SPI channel and the GPIOs will still remain occupied though; for a clean closing use "shutdown".

        """
        if status:
            gpio.output(self.pwdn, 1)
        elif not status:
            gpio.output(self.pwdn, 0)
        else:
            raise ValueError('Choose either True(1)/False(0) as the power status of the ADC.')

    def shutdown(self):
        """
        Inactivating the temperature module, shutting down the ADC, closing the SPI channel and releasing the GPIOs.
        """
        if gpio.getmode() is None:
            pass
        else:
            gpio.output([self.tmp, self.pwdn], 0)
        self.spi.close()
        gpio.cleanup()

    def data_ready(self):
        if self._miso is None:
            raise RuntimeError('No GPIO pins was assigned to monitor the MISO pin.')
        else:
            return True if not gpio.input(self._miso) else False

    def read(self, gain=1, speed=0, channel=1):
        """
        [DATA FORMAT] from the datasheet (page 18)
        "The ADS1232/4 output 24 bits of data in binary two’s complement format. The least significant bit (LSB) has
         a weight of 0.5VREF/(2**23 – 1). The positive full-scale input produces an output code of 7FFFFFh and
         the negative full-scale input produces an output code of 800000h."

        gain [1, 2, 64, 128] will be configured using the two gain pins (g0, g1):
        gain      g0      g1
        [1]  :     0       0
        [2]  :     1       0
        [64] :     0       1
        [128]:     1       1

        speed [0, 1] will set the data retrieval rate to either 10SPS or 80SPS by pulling the SPEED pin to Low or High.
        channel [1, 2] could be used to select the AIN1 or AIN2 input channels.
        """
        gpio.cleanup(self._sclk)
        if not gpio.input(self.pwdn):  # checks the PWDN pin, if in Low status, pulls it High.
            gpio.output(self.pwdn, 1)
        if gpio.input(self.tmp):  # checks the TEMP pin, if in High status, pulls it Low.
            gpio.output(self.tmp, 0)

        if gain not in [1, 2, 64, 128]:
            raise ValueError('Gain has to be a value among [1, 2, 64, 128].')
        gain_mode = {
            1: (0, 0),
            2: (1, 0),
            64: (0, 1),
            128: (1, 1)}
        gpio.output((self.g0, self.g1), gain_mode[gain])

        if speed not in [0, 1]:
            raise ValueError('Speed has to be either 0 or 1.')
        gpio.output(self.spd, 1) if speed == 1 else gpio.output(self.spd, 0)

        if self._mux is not None:
            if channel not in [1, 2]:
                raise ValueError('Input channel has to be selected by either 1 or 2 for the AIN1/AIN2 channels.')
            else:
                gpio.output(self._mux, 1) if channel == 2 else gpio.output(self._mux, 0)

        dummy_bytes = self.spi.xfer2([0, 0, 0])
        if self.data_ready():
            print((((dummy_bytes[0] & 0x7F) << 16) + (dummy_bytes[1] << 8) + (dummy_bytes[2])) * self.vref / 8388607)

    def read_temp(self, gain=1):
        """
        Setting the TEMP pin to High disconnects the analog inputs to the ADC and activates the two internal diodes.
        Measuring the voltage difference of these two diodes can be interpreted for temperature measurements.
        from the datasheet:
        "Typically, the difference in diode voltage is 111.7mV at 25°C with a temperature coefficient of 379µV/°C.
        With PGA = 1 and 2, the difference voltage output from the PGA will be 111.7mV and 223.4mV, respectively.
        With PGA = 64 and 128, it is impossible to use the temperature sensor function."
        """
        gpio.cleanup(self._sclk)
        if not gpio.input(self.pwdn):  # checks the PWDN pin, if in Low status, pulls it High.
            gpio.output(self.pwdn, 1)
        if gain not in [1, 2]:
            raise ValueError('Gain in temperature-measurement mode must be either 1 or 2.')
        gpio.output((self.g0, self.g1), (0, 0)) if gain == 1 else gpio.output((self.g0, self.g1), (1, 0))
        gpio.output(self.tmp, 1)
        diff_g1, diff_g2 = 111.7e-3, 223.4e-3
        temp_coeff = 379e-6
        
        dummy_bytes = self.spi.xfer2([0, 0, 0])
        if self.data_ready():
            rsp = (((dummy_bytes[0] & 0x7F) << 16) + (dummy_bytes[1] << 8) + (dummy_bytes[2])) * self.vref / 8388607
            print(rsp)
            if gain == 1:
                print("Temperature: {} C".format(((rsp - diff_g1) / temp_coeff) + 25))
            if gain == 2:
                print("Temperature: {} C".format(((rsp - diff_g2) / temp_coeff) + 25))
            
ads = ADS1232()
ads.offset_calibration()
while True:
    try:
        ads.read(gain=1)
        #ads.read_temp()
        time.sleep(0.2)
    except KeyboardInterrupt:
        ads.shutdown()
        print('aborted!')
        break
    except Exception as e:
        ads.shutdown()
        print(e)
        break
