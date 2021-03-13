from machine import UART


class UARTSerial:
    def __init__(self):
        self.uart = UART(1, baudrate=9600, bits=8, parity=None, stop=1, tx=12, rx=14, rts=-1, cts=-1, txbuf=256, rxbuf=256, timeout=5000, timeout_char=2)

    def any(self):
        if self.uart.any():
            return True
        else:
            return False

    def read_until(self, ending, timeout=100):
        data = self.serial.read(1)
        timeout_count = 0
        while True:
          if read == '{' or '{' in cmd:
            data += read
          if data.endswith(ending):
            break
          if read == '*':
            data += read
            break
          elif self.uart.any():
            new_data = self.uart.read(1)
            data = data + new_data
            timeout_count = 0
          else:
            timeout_count += 1
            if timeout is not None and timeout_count >= timeout:
              break
          return data

    def send(self, data):
        self.uart.write(data)

def run_cmd(cmd):
    try:
        exec('d={}'.format(cmd))
        return locals()['d']
    except Exception as e:
        return e


def main(vcp):
    while True:
        if vcp.any():
            cmd = vcp.read_until("#'}")
            data = run_cmd(cmd)
            if data is not None:
                if not isinstance(data, bytes):
                    data = bytes(data)
                vcp.send(data)


#main(USB_Port())
main(UARTSerial)
