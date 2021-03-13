import time
import RPi.GPIO as gpio

gpio.setmode(gpio.BCM)
gpio.setup(26, gpio.OUT)
for _ in range(5):
    gpio.output(26, 1)
    time.sleep(1)
    gpio.output(26, 0)
    time.sleep(1)
gpio.cleanup()

print("code ended here.")


