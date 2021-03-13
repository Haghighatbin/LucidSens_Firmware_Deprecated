import network, machine, utime
counts = 0
station = network.WLAN(network.STA_IF)
essid = 'ECL&CL'
password = 'ecl326326'

def auth_mode(mod):
    lst = {0: 'open',
           1: 'WEP',
           2: 'WPA-PSK',
           3: 'WPA2-PSK',
           4: 'WPA/WPA2-PSK'
           }
    return lst.get(mod)

def hidden(mod):
    lst = {False: "visible",
           True: "hidden"}
    return lst.get(mod)
    
station.active(True)
utime.sleep(3)
print("w_thread: scanning network...")
print("SSID                            Channel    RSSI    AuthMode    Hidden/Visible" + "\n")
for i in station.scan():
    print("{}:{}                  {}          {}          {}          {}".format(counts, i[0].decode(), i[2], i[3], auth_mode(i[4]), hidden(i[5])))
    counts += 1
    utime.sleep(0.5)
print("w_thread: connecting to the pre-defined:\nessid: {}\npassword: {}\n".format(essid, password))
station.connect(essid, password)
utime.sleep(5)

if station.isconnected():
    print("Connection established.")
    station.config('mac')
    # print("executing ifconfig command")
    station.status()
    print("setting up the static IP")
    
else:
  print('wifi still not connected')
print('initializing the telnet')

network.telnet.start()
print('telnet status: {}'.format(network.telnet.status())) # IP from here -- username:micro pass:python
utime.sleep(5)
# network.ftp.start()
# network.ftp.status()

