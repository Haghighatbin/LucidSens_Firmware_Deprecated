from machine import ADC, DAC, Pin, PWM
from time import sleep
import _thread
from array import array

dac = DAC(25)
dac.write(96)
adc = ADC(34)
adc.atten(ADC.ATTN_11DB)


# Sine lighting 
def th_adc_read():
  print('adc reading thread initiated.')
  _thread.allowsuspend(True)
  while True:
    ntf = _thread.getnotification()
    if ntf:
      if ntf == _thread.EXIT:
        print('received EXIT notification.')
        adc.deinit()
        print('adc.released.')
        return
      elif ntf == _thread.SUSPEND:
        while _thread.wait != _thread.RESUME:
          pass
      #elif ntf == myownntf:
      #  pass 
      else:
        pass
    a = array('h', 20)
    adc.collect(2000, data=a)
    sleep(0.02)
    if not adc.progress()[0]:
      print('sampling done')
      print('array: {}'.format(a))
      print('Summary: {}'.format(adc.collected()))
      print('Average: {}'.format(adc.collected()[2]))
      # adc.stopcollect()
    else:
      print('sampling in progress.')
      
    print('read function: {}'.format(adc.read()))
    print('---------------------')
    sleep(0.1)
      
def th_signal():
  while True:
    print('Signalling thread initiated.')
    _thread.allowsuspend(True)
    pwm = PWM(12)
    for _ in range(1):
      for i in range(99):
        pwm.duty(i)
        sleep(0.1)
      for j in range(99, 0, -1):
        pwm.duty(j)
        sleep(0.1)
      sleep(3)
    #pwm.duty(1)
    print("done with sending signals.")
    pwm.deinit()
    for thread in _thread.list(False):
      if thread[0] != _thread.getMainID():
        _thread.notify(thread[0], _thread.EXIT)
        print('notified the adc_reading thread to EXIT.')
    for thread in _thread.list(False):
      if thread[2] == 'signaler':
        return

try:
  _thread.start_new_thread('adc_reading', th_adc_read, ())
  _thread.start_new_thread('signaler', th_signal, ())

  while True:
    if len(_thread.list(False)) == 1:
      print('threads were closed.')
      break
    else:
      pass  
      
  dac.write(0)
  dac.deinit()
  adc.deinit()
  print('dac/adc are released.')
except KeyboardInterrupt:
  dac.write(0)
  dac.deinit()
  adc.deinit()
  for thread in _thread.list(False):
    _thread.stop(thread[0])
  print('aborted.')
except:
  dac.write(0)
  dac.deinit()
  for thread in _thread.list(False):
    _thread.stop(thread[0])
  print('shutting down.')
  

# Create a array for 40000 audio samples (8-bit)
#a=array('B', 400)



# Collect 4 seconds of data (record audio) at 10000 samples/second
#adc.collect(100, data=a)
# After 4 seconds check the progress and the collected data info
# adc.progress()
#(False, 40000, 40000, 3999985)
#adc.collected()
#(0, 4095, 1951, 2424)
# Stop the sine wave and reproduce the collected data on DAC output
#dac.stopwave()
#dac.write_buffer(a, 10000)
 
  
  









