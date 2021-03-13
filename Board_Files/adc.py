from machine import ADC
from array import array
from utime import ticks_ms, ticks_diff, sleep_ms


class Sampler:
    def __init__(self, pin):
        self.adc = ADC(pin)
        if pin == 36:
            self.mode = 'hv'
            # print('ADC is now sampling in {} mode.'.format(self.mode.upper()))
        elif pin in [34, 39]:
            self.mode = 'sipm'
            # print('ADC is now sampling in {} mode.'.format(self.mode.upper()))
        else:
            raise RuntimeError('Invalid pin definition or wrong call.')
        self.adc.atten(ADC.ATTN_11DB)

    def sampler(self, acquisition=3, intervals=0.1, raw_to_avrg=10):
        """
        :param acquisition: ADC total reading time in seconds
        :param intervals: sampling intervals in seconds
        :param raw_to_avrg: number of raw samples to be picked and averaged between two intervals
        returns an array[list] of ADC reads
        """
        def calibration(data):
            if self.mode == 'hv':
                return (data + 95.68)/78.14
            elif self.mode == 'sipm':
                return (data + 183.7)/1276.1
            else:
                raise RuntimeError('Invalid pin definition or wrong call.')
        frq = int(raw_to_avrg / intervals)
        datapoint = array('H', raw_to_avrg)
        true_set = array('d')
        calib_set = array('d')
        start_tot = ticks_ms()
        for _ in range(int(acquisition/intervals)):
            self.adc.collect(freq=frq, data=datapoint)
            start = ticks_ms()
            while True:
                try:
                    if not self.adc.progress()[0]:
                        end = ticks_ms()
                        true_val = self.adc.collected()[2]
                        calib_val = calibration(self.adc.collected()[2])
                        # print('{} ms took to collect one averaged data-point.'.format(ticks_diff(end, start)))
                        true_set.append(true_val)
                        calib_set.append(calib_val)
                        break
                    else:
                        pass
                except KeyboardInterrupt:
                    # print('aborted.')
                    self.adc.deinit()
                    break
                except Exception as e:
                    self.adc.deinit()
                    print(e)
                    break
        end_tot = ticks_ms()
        # print('{} ms took to collect the true_set.'.format(ticks_diff(end_tot, start_tot)))
        # print('true val: {}'.format(sum(true_set)/len(true_set)))
        # print('calib val: {}'.format(sum(calib_set)/len(calib_set)))

        return calib_set

    def deinit(self):
        self.adc.deinit()
        # return 'ADC module deinitialized.'



