try:
    f = open("account.txt", 'r')
    for lines in f:
        for line in lines.split('\r'):
            if "#" in line:
                pass
            elif "ip" in line:
                ip = line.split(' ')[2]
            elif "port" in line:
                port = int(line.split(' ')[2])
            elif "subnet" in line:
                subnet = line.split(' ')[2]
            elif "gateway" in line:
                gateway = line.split(' ')[2]
            elif "dns" in line:
                dns = line.split(' ')[2]
            elif "essid" in line:
                essid = line.split(' ')[2]
            elif "password" in line:
                password = line.split(' ')[2]
            else:
                print("\nw_thread: something wrong with the account file...")
                pass
    print("\nw_thread: done getting wifi credentials...")
    f.close()

except Exception as e:
    print("\nw_thread: something wrong with the account file...\n")
    print(e)
    pass
