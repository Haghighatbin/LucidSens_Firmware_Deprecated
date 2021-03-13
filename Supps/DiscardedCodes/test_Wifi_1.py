import network
import ujson
import socket
import sys


def connect():
    ip = '192.168.1.93'  # Static IP
    port = 3175
    subnet = '255.255.255.0'
    gateway = '192.168.1.1'
    dns = '8.8.8.8'
    essid = "nahaangard"
    password = "Amin_3175!?$"

    station = network.WLAN(network.STA_IF)

    if station.isconnected():
        print("Wifi already connected! DONE.")
        print()
        print("Creating the socket")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket is created...listening to the incoming calls...")
        sock.bind((ip, port))
        communicate(sock)

    station.active(True)
    print("Scanning network...")
    station.scan()
    print("Connecting to the essid: {}".format(essid))
    station.connect(essid, password)
    print("Connection established.")
    station.config('mac')
    print("executing ifconfig command")
    station.ifconfig()
    print("Disconnecting to setup a static IP")
    station.disconnect()
    print("Successfully disconnected.")
    station.status()
    print("Setting up the static IP")
    station.ifconfig((ip, subnet, gateway, dns))
    print("Reconnecting...")
    station.connect()
    print("Wifi successfully connected. DONE.")
    print("re-executing ifconfing command:")
    print(station.ifconfig())

    while not station.isconnected():
        pass
    print()
    print("Creating the socket")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket is created...listening to the incoming calls...")
    sock.bind((ip, port))
    communicate(sock)


def communicate(sock):
    try:
        while True:
            sock.listen(1)
            conn, addr = sock.accept()

            if conn:
                conn.sendall("Wifi connection established, waiting for the calls...".encode())
                print("Received a call from: {}".format(addr))
                while True:
                    cmd = conn.recv(1024).decode()
                    if not cmd:
                        sock.close()
                        break
                    print("{} command was received!".format(cmd))
                    if cmd == 'w':
                        conn.sendall("Wifi is already connected, proceed.".encode())
                    elif cmd == 'a':
                        n = 10
                        data = {"data_Header": "Test_Asteroid"}
                        data.update({"data_value": [[(i, 0), (0, abs(abs(i) - n)), (0, -(abs(abs(i) - n)))] for i in
                                                    range(-n, n + 1)]})
                        data.update({"data_Footer": "DONE."})
                        encoded_data = ujson.dumps(data)
                        conn.sendall(encoded_data)
                    elif cmd == 'd':
                        disconnect()
                    else:
                        sock.close()
                        break

    except:
        return


def disconnect():
    station = network.WLAN(network.STA_IF)
    station.disconnect()
    print("Wifi disconnected. DONE.")
    station.active(False)
