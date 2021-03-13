from machine import PWM
from time import sleep


def main():
    pwm = PWM(26)
    pwm.freq(10000)
    for i in range(0, 100, 10):
        pwm.duty(i)
        sleep(0.5)
    for j in range(100, 0, -10):
        pwm(j)
        sleep(0.5)
    pwm.duty(0)


if __name__ == '__main__':
    main()



