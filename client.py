import time

import cv2
import socket
import numpy as np
import YB_Pcb_Car


# dmdkkdk
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("172.20.10.4", 8888))
print("client connected")

cam = cv2.VideoCapture(0)

cam.set(3, 640)
cam.set(4, 480)

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
car = YB_Pcb_Car.YB_Pcb_Car()
count = 0
while True:
    try:
        ret, frame = cam.read()
        result, frame = cv2.imencode('.jpg', frame, encode_param)
        send_data = np.array(frame)
        stringData = send_data.tostring()

        client_socket.sendall((str(len(stringData))).encode().ljust(16) + stringData)

        time.sleep(0.1)
        recv_stringData = client_socket.recv(16)

        if (recv_stringData):
            recv_data = np.fromstring(recv_stringData, dtype='uint8')
            received_data = recv_data.tolist()
            count += 1
            print(count, 'Received', received_data[0], received_data[8])
            time.sleep(0.05)
            car.Car_Run(received_data[0], received_data[8])
            time.sleep(0.05)

    except Exception as e:
        car.Car_Stop()
        print("client-client", e)
        # continue
        exit(0)
    except KeyboardInterrupt:
        cam.release()
        car.Car_Stop()
        client_socket.close()
        exit(0)
        print("terminated..")

