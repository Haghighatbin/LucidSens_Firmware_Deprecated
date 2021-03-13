from machine import ADC
from array import array
from utime import ticks_ms, ticks_diff, sleep_ms


class AdcSampler:
    def __init__(self, pin):
        self.adc = ADC(pin)
        self.adc.atten(ADC.ATTN_11DB)
        self.datapoint = array('H', 50)

    def hv_sampler(self, samples):
        dataset = array('d')
        for _ in range(samples):
            self.adc.collect(freq=200, data=self.datapoint)
            start = ticks_ms()
            while True:
                try:
                    if not self.adc.progress()[0]:
                        end = ticks_ms()
                        print('single-point samping is done.')
                        print('ADC measured {} V'.format(self.adc.collected()[2] / 1000))
                        true_val = (self.adc.collected()[2] + 110)/58.85
                        print('Estimated HV {:.1f} V'.format(true_val))
                        print('{} ms took to collect one averaged data-point.'.format(ticks_diff(end, start)))
                        print('#---------------------------------------------#')
                        dataset.append(true_val)
                        break
                    else:
                        pass
                except KeyboardInterrupt:
                    print('aborted.')
                    self.adc.deinit()
                    break
                except Exception as e:
                    self.adc.deinit()
                    print(e)
                    break
            sleep_ms(750)
        readV = sum(dataset)/len(dataset)
        print('Average value: {:.1f} V'.format(readV))
        # return 'averaged dataset:\n{}'.format(dataset)
        if round(readV, 2) < 3.00:
            return 0
        else:
            return readV

    def fmode_sampler(self):
        pass

    def smode_sampler(self):
        pass

    def deinit(self):
        self.adc.deinit()
        # return 'ADC module deinitialized.'



