import sys
import _thread
import socket
import ujson
import network
import sys

# import main_Wifi
ip = '192.168.1.93'  # Static IP
port = 3175
subnet = '255.255.255.0'
gateway = '192.168.1.1'
dns = '8.8.8.8'
essid = "nahaangard"
password = "Amin_3175!?$"


def wifi_handler():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, port))
    while True:

        try:
            print('Wifi thread: waiting for the incoming calls...')
            sock.listen(20)
            conn, addr = sock.accept()
            # conn.sendall("Wifi connection established, waiting for the calls...".encode())
            while True:
                if conn:
                    print("Received a call from: {}".format(addr))
                    cmd = conn.recv(1024).decode()

                    if not cmd:
                        break
                    # print("{} command was received!".format(cmd))

                    if cmd == 'w':
                        conn.sendall("Wifi is already connected, proceed.".encode())

                    elif cmd == 'a':
                        n = 15
                        data = {"data_Header": "Test_Asteroid"}
                        data.update({"data_value": [[(i, 0), (0, abs(abs(i) - n)), (0, -(abs(abs(i) - n)))] for i in
                                                    range(-n, n + 1)]})
                        data.update({"data_Footer": "DONE."})
                        encoded_data = ujson.dumps(data)
                        conn.sendall(encoded_data)
                        # sock.close()
                        # print(encoded_data)
                        # print("asteroid was sent.")
                    elif cmd == 'd':
                        # print('received message to shutdown the Wifi thread...')
                        conn.sendall(b'MinimalSens: Wifi is shutting down.')
                        wifi_disconnect()
                        _thread.exit()
                        break

                    else:
                        print("Invalid command.")
                        pass
                else:
                    print("Closing socket in inner while")
                    sock.close()
                    break

        except Exception as e:
            print(e)
            print("Closing socket in try.")
            sock.close()
            break


def wifi_connection():
    station = network.WLAN(network.STA_IF)

    if station.isconnected():
        print("Wifi is already connected.")
        return True
    station.active(True)
    # print("Scanning network...")
    station.scan()
    # print("Connecting to the essid: {}".format(essid))
    station.connect(essid, password)
    # print("Connection established.")
    station.config('mac')
    # print("executing ifconfig command")
    station.ifconfig()
    # print("Disconnecting to setup a static IP")
    station.disconnect()
    # print("Successfully disconnected.")
    station.status()
    # print("Setting up the static IP")
    station.ifconfig((ip, subnet, gateway, dns))
    # print("Reconnecting...")
    station.connect()
    print("Wifi successfully connected.")
    # print("re-executing ifconfing command:")
    # print(station.ifconfig())
    return True


def wifi_disconnect():
    station = network.WLAN(network.STA_IF)
    station.disconnect()
    print("Wifi disconnected.")
    station.active(False)
    return

