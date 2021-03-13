import usocket as socket
import network
import utime
from upysh import *
import sys
from machine import Pin
import o
import ujson as json


# ip = '192.168.0.95'
# port = 3175
# subnet = '255.255.255.0'
# gateway = '192.168.1.1'
# dns = '208.67.222.222'
# #essid = 'TP-LINK_CFF1'
# #password = 'ecl534534'
# essid = 'tplink'
# password = 'Amin_3175!?$'

class WifiConnection:
    def __init__(self):
        self.p_led = Pin(2, Pin.OUT)
        self.clear = clear
        try:
            f = open("account.txt", 'r')
            for lines in f:
                for line in lines.split('\r'):
                    if "#" in line:
                        pass
                    elif "ip" in line:
                        self.ip = line.split(' ')[2]
                    elif "port" in line:
                        self.port = int(line.split(' ')[2])
                    elif "subnet" in line:
                        self.subnet = line.split(' ')[2]
                    elif "gateway" in line:
                        self.gateway = line.split(' ')[2]
                    elif "dns" in line:
                        self.dns = line.split(' ')[2]
                    elif "essid" in line:
                        self.essid = line.split(' ')[2]
                    elif "password" in line:
                        self.password = line.split(' ')[2]
                    else:
                        # print("\nw_thread: something wrong with the account file...")
                        pass
            print("\nw_thread: done getting wifi credentials...")
            f.close()

        except Exception as e:
            print("\nw_thread: something wrong with the account file...\n")
            print(e)
            pass

    def wf_handler(self):
        opr = o.Operator()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.ip, self.port))
        while True:
            try:
                self.clear
                print('\nw_thread: READY.')
                sock.listen(5)
                conn, addr = sock.accept()
                while True:
                    try:
                        if conn:
                            print("w_thread: received a call from: {}".format(addr))
                            print("w_thread: sending command to operator...")
                            cmd = conn.recv(4096).decode()
                            parsed_cmd = json.loads(cmd)
                            if parsed_cmd['header'] in ['run', 'tst']:
                                conn.sendall(opr.operator_func(parsed_cmd))
                                print('w_thread: response is sent.')
                                break
                                # sock.close()
                            else:
                                # sock.close()
                                break
                        else:
                            print("w_thread: something went run with the connection!")
                            # sock.close()
                            break
                    except KeyboardInterrupt:
                        print("\nw_thread: aborted by user!")
                        break
                    except Exception as e:
                        print(e)
                        break

            except KeyboardInterrupt:
                print("\nw_thread: aborted by user!")
                sock.close()
                break

            except Exception as e:
                print(e)
                print("w_thread: closing socket in try_receiver.")
                sock.close()
                break

    def wf_connection(self):
        counts = 0
        station = network.WLAN(network.STA_IF)
        try:
            if station.isconnected():
                print(station.ifconfig())
                print("w_thread: wifi is already connected.")
                self.p_led.value(1)
                return station.isconnected()

            else:
                station.active(True)
                print("w_thread: wifi has not been connected yet.")
                utime.sleep(3)
                print("w_thread: scanning network...")

                scanned = station.scan()
                modified_scanned_list = [list(j for idx, j in enumerate(signal) if idx not in [1, 4, 6]) for signal in scanned]
                header = ['ESSID', 'Channel', 'RSSI', 'AuthMode']
                row_format = "|{:^30}|" * (len(header))
                print(128 * '-')
                print(row_format.format(*header))
                print(128 * '-')
                print('\n'.join(row_format.format(*row) for row in modified_scanned_list))
                print(128 * '-', '\n')

                print("w_thread: connecting to the pre-defined:\nessid: {}\npassword: {}\n".format(self.essid, self.password))
                station.connect(self.essid, self.password)
                utime.sleep(3)

            if station.isconnected():
                # print("Connection established.")
                station.config('mac')
                # print("executing ifconfig command")
                station.status()
                # print("setting up the static IP")
                station.ifconfig((self.ip, self.subnet, self.gateway, self.dns))
                # print("re-executing ifconfig command:")
                print(station.ifconfig())
                self.p_led.value(1)
            return station.isconnected()

        except Exception as e:
            print(e)
            return station.isconnected()

    def wf_disconnect(self):
        station = network.WLAN(network.STA_IF)
        station.disconnect()
        print("w_thread: wifi is not connected.")
        station.active(False)
        self.p_led.value(0)
        return

    def auth_mode(self, mod):
        lst = {0: 'open',
               1: 'WEP',
               2: 'WPA-PSK',
               3: 'WPA2-PSK',
               4: 'WPA/WPA2-PSK'
               }
        return lst.get(mod)

    def hidden(self, mod):
        lst = {False: "visible",
               True: "hidden"}
        return lst.get(mod)

    def __str__(self):
        print("WiFiConn class is activated.")

