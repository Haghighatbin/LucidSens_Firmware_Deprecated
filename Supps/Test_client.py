import socket
import sys


def main():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = "127.0.0.1"
    port = 8888
    print("Socket created.")
    try:
        soc.connect((host, port))
        print("connection established.")
    except:
        print("Connection error")
        sys.exit()

    print("Enter 'quit' to exit")
    message = input(str(" -> "))

    while message != 'quit':
        soc.sendall(message.encode())
        print(soc.recv(5120).decode())
        message = input(" -> ")

    # soc.send(b'--quit--')


if __name__ == '__main__':
    main()

