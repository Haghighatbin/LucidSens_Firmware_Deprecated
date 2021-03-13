from machine import SPI, Pin


class ADS1232:
    """
    DVDD, AVDD, RefP >> VDD
    DGND, CLKIN, Gain, RefN, AGND, Speed, AINN1-2, XTAL1-2 >> GND
    CAPS >> connected to each other with a 220 nF cap (bridged)
    AINP >> I'm using a a simple Light-dependent resistor(LDR) to provide an analog signal
    DRDY/DOUT >> MISO
    MOSI unconnected
    SCLK >> SCLK
    A0 >> GND reads AINP1 ---- A0 >>
    
    The hardware SPI host
    (1) machine-SPI.HSPI (1) 
    (2) machine.SPI.VSPI (2) Default: 1
    """

    def __init__(self, pwdn_pin=15, g0_pin=21, g1_pin=22, tmp_pin=4, spd_pin=2, clk=18, miso=19, mosi=23, vdd=5):
        """
        Initialize ADS1232 device with software SPI on the specified CLK,
        CS, and DO pins.
        """
        self._g0 = Pin(g0_pin, Pin.OUT)  # 21
        self._g1 = Pin(g1_pin, Pin.OUT)  # 22
        self._pwdn = Pin(pwdn_pin, Pin.OUT)  # 15
        self._spd = Pin(spd_pin, Pin.OUT)  # 2
        self._smp_t = 0.5  # sampling intervals
        self._VDD = vdd
        if tmp_pin is not None:
            self._tmp = Pin(tmp_pin, Pin.OUT)  # 4
        else:
            self._tmp = tmp_pin
        self._spi = SPI(spihost=2, baudrate=1000000, polarity=0, phase=0, firstbit=SPI.MSB, sck=clk,
                        miso=miso, mosi=mosi, duplex=True)

    def operator(self, power='off', gain=1, speed=0):
        self._pwdn.value(1) if power == 'on' else self._pwdn.value(0) if power == 'off' else self._pwdn.value(0)
        print('power is set.')
        if gain == 1:
            self._g0.value(0)
            self._g1.value(0)
            print('gain is set')
        elif gain == 2:
            self._g0.value(1)
            self._g1.value(0)
        elif gain == 64:
            self._g0.value(0)
            self._g1.value(1)
        elif gain == 128:
            self._g0.value(1)
            self._g1.value(1)
        else:
            self._g0.value(0)
            self._g1.value(0)
            raise ValueError('The valid gain values are 1, 2, 64, 128. (Default=1)')
        self._spd.value(1) if speed == 1 else self._spd.value(0)
        print('speed is set.')
        return

    def read(self, gain, speed):
        self.operator(power='on', gain=gain, speed=speed)
        rd_buf = bytearray(12)
        print('rd_buf: {}'.format(rd_buf))
        wr_buf = bytearray([0,0,0])
        print('reading: ')
        self._spi.write_readinto(wr_buf, rd_buf)
        print(self._spi.write_readinto(wr_buf, rd_buf))
        print(rd_buf, type(rd_buf))
        resp = (((rd_buf[0] & 0x7F) << 16) + (rd_buf[1] << 8) + (rd_buf[2]))  # * self._VDD / float(8388607)
        return resp

    def read_tmp(self, g):
        gain = g if g in [1, 2] else 1
        speed = self._spd.value()
        self.operator(power='on', gain=gain, speed=speed)
        self._tmp.value(1)
        """"""


