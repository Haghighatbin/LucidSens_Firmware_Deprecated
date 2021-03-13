import sys
import ujson


def usb_handler():
    while True:
        try:
            # print('USB thread: waiting for the incoming calls...')
            cmd = sys.stdin.read(1)
            if cmd == 'a':
                # print('received a')
                # print(test_asteroid())
                # print(operator_func[cmd])
                n = 15
                data = {"data_Header": "Test_Asteroid"}
                data.update({"data_value": [[(i, 0), (0, abs(abs(i) - n)), (0, -(abs(abs(i) - n)))] for i in
                                            range(-n, n + 1)]})
                data.update({"data_Footer": "DONE."})
                encoded_data = ujson.dumps(data)
                print(encoded_data)
        except:
            break
