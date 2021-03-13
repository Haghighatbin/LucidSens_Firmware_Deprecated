import sys
import _thread
import socket
import ujson
import network

import wifi_mod
import usb_mod

ip = '192.168.1.93'  # Static IP
port = 3175
subnet = '255.255.255.0'
gateway = '192.168.1.1'
dns = '8.8.8.8'
essid = "tplink"
password = "Amin_3175!?$"


def test_asteroid():
    n = 15
    data = {"data_Header": "Test_Asteroid"}
    data.update({"data_value": [[(i, 0), (0, abs(abs(i) - n)), (0, -(abs(abs(i) - n)))] for i in range(-n, n + 1)]})
    data.update({"data_Footer": "DONE."})
    encoded_data = ujson.dumps(data)
    return encoded_data


operator_func = {
    'a': test_asteroid()
}


def main():
    wifi_mod.wifi_connection()
    try:
        # print("Wifi thread launched")
        _thread.start_new_thread(wifi_mod.wifi_handler, ())
        # print('USB thread launched.')
        _thread.start_new_thread(usb_mod.usb_handler(), ())

    except:
        pass


if __name__ == '__main__':
    main()
