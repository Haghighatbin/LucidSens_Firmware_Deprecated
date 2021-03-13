import machine, utime

adc = machine.ADC(machine.ADC.HALL)


def read():
    return adc.read()


def hall_read(iter=100, intrvl=0.1):
    for _ in range(iter):
      try:
          print(read())
          utime.sleep(intrvl)
      except KeyboardInterrupt:
          print('aborted!')
          adc.deinit()
      except Exception as e:
          print(e)
          adc.deinit()


