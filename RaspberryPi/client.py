import time

import cv2
import socket
import numpy as np
import YB_Pcb_Car   # 구매한 RC카 업체에서 제공하는 바퀴 제어 모듈
from avoid import avoid
from stopline import restricting

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("172.20.10.4", 8888))
print("client connected")

cam = cv2.VideoCapture(0)

cam.set(3, 640)
cam.set(4, 480)

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
car = YB_Pcb_Car.YB_Pcb_Car()
count = 0
stop_flag = False
while True:
    try:
        ret, frame = cam.read()
        result, frame = cv2.imencode('.jpg', frame, encode_param)
        send_data = np.array(frame)
        stringData = send_data.tostring()

        client_socket.sendall((str(len(stringData))).encode().ljust(16) + stringData)

        recv_stringData = client_socket.recv(16)

        if avoid():  # 장애물 인식
            car.Car_Stop()
            continue
        stopline_flag = restricting()

        if recv_stringData:
            recv_data = np.fromstring(recv_stringData, dtype='uint8')
            received_data = recv_data.tolist()

            if stopline_flag == 1:                                 # 정지선 인식 (교차로)
                car.Car_Stop()
                print("stop line")
                time.sleep(0.1)
                if received_data[0] == 10 and received_data[8] == 10:  # 빨간불
                    car.Car_Stop()
                    print("red light!!!!!!!!!!!!!!!")
                    continue
                elif received_data[0] == 21 and received_data[8] == 21:  # 좌회전
                    print("Go Left!!!!!!!!!!!!!!!")
                    car.Car_Run(30, 90)     # 왼쪽으로 회전시켜주기
                    time.sleep(2)
                elif received_data[0] == 22 and received_data[8] == 22:  # 우회전
                    print("Go Right!!!!!!!!!!!!!!!")
                    car.Car_Run(87, 30)     # 오른쪽으로 회전시켜주기
                    time.sleep(2)
                continue    # 아무것도 인식 못함 -> 다시

            if received_data[0] == 0 and received_data[8] == 0:  # 라인 인식 못함
                print("no line detected*************")
                continue

            if received_data[0] == 10 and received_data[8] == 10:  # 빨간불
                car.Car_Stop()
                stop_flag = True
                print("red light!!!!!!!!!!!!!!!")
                continue

            elif received_data[0] == 40 and received_data[8] == 40:  # 초록불
                stop_flag = False
                print("Green light!!!!!!!!!!!!!!!")

            if not stop_flag:   # 달리기 (빨간불 아니면)
                count += 1
                print(count, 'Received', received_data[0], received_data[8], stopline_flag)

                # PC에서 받은 양쪽 바퀴 속도 + 적외선으로 주행 보조
                if stopline_flag == 2:
                    car.Car_Run(received_data[0] + 10, received_data[8])
                elif stopline_flag == 3:
                    car.Car_Run(received_data[0] + 20, received_data[8])
                elif stopline_flag == 4:
                    car.Car_Run(received_data[0], received_data[8] + 20)
                elif stopline_flag == 5:
                    car.Car_Run(received_data[0], received_data[8] + 30)
                else:
                    car.Car_Run(received_data[0], received_data[8])

    except Exception as e:
        print("client-client Exception", e)
        continue

    except KeyboardInterrupt:
        cam.release()
        car.Car_Stop()
        client_socket.close()
        exit(0)
        print("terminated..")
