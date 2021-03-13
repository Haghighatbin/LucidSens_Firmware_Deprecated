import utime
from machine import Pin, DHT

p_rfan = Pin(2, Pin.OUT)
p_peltierI = Pin(23, Pin.OUT)
p_peltierII = Pin(19, Pin.OUT)
p4 = Pin(4)
dht = DHT(p4, DHT.DHT2X)

target_temp = 37
last_measurement_ms = 0

while True:
    try:
        if utime.ticks_diff(utime.ticks_ms(), last_measurement_ms) >= 10000:
            (success, current_temp, humid) = dht.read()
            if success:
                print('Temperature: {} C'.format(current_temp))
                # Heating process
                if current_temp < int(target_temp - 2):
                    if p_peltierI.value():
                        pass
                    else:
                        p_peltierI.value(1)
                        print('heating module activated.')

                elif current_temp == int(target_temp - 2):
                    print('heating module deactivated.')
                    p_peltierI.value(0)

                # Cooling process
                if current_temp > int(target_temp + 2):
                    if p_peltierII.value():
                        pass
                    else:
                        p_peltierII.value(1)
                        print('cooling module activated.')
                    p_rfan.value(1)
                elif current_temp == int(target_temp + 2):
                    p_peltierII.value(0)
                    print('cooling module deactivated.')
                    p_rfan.value(0)
                last_measurement_ms = utime.ticks_ms()

            else:
                print('Temp. sensor returns wrong values!')
                pass
        else:
            pass

    except KeyboardInterrupt:
        p_peltierI.value(0)
        p_peltierII.value(0)
        print('\npeltier drivers turned off.')
        p_rfan.value(0)
        print('read fan turned off.')
        p4.value(0)
        raise
    except Exception as e:
        print(e)
        pass
