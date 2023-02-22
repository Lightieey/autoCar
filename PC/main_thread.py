import cv2
import time
import socket
import numpy as np
import threading
from line_detection import line_detection
from light_detection import light_detection
from signdetector import sign_detection

# 전역 변수
BASE = 40
SIGN_ADD = 0
num_line = 0
num_signal = 0
num_sign = 0
signal = 'go'
sign = 'Not Found'
frame = []
left = 0
right = 0
line_count = 2

lined_frame = []
sign_frame = []
signal_frame = []

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

HOST='172.20.10.4'
PORT=8888

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("socket created")

server_socket.bind((HOST, PORT))
print("socket bind complete")

server_socket.listen(10)
print("socket new listening")

client_socket, addr = server_socket.accept()


def line_detect():
    global frame, left, right, line_count, num_line, lined_frame
    while True:
        try:
            slope, lined_frame, line_count = line_detection(frame)

            filename = f"./images_1217/frame{num_line}.jpg"
            cv2.imwrite(filename, lined_frame)

            left, right = get_speed(slope)
            print(f'[line] {num_line}th slope: {slope}', end="")
            print(f'left: {left}, right: {right}')
            time.sleep(0.05)

            num_line += 1

        except Exception as e:  # line 인식 못했을 때
            # 신호등 확인
            left = 0
            right = 0
            check_sign()
            continue




def signal_detect():
    global signal, num_signal, frame, signal_frame
    while True:
        signal, signal_frame = light_detection(frame)
        filename = f"./images_signal/frame{num_signal}.jpg"
        cv2.imwrite(filename, signal_frame)
        print(f'[signal] {num_signal}th: {signal}')
        num_signal += 1
        time.sleep(0.05)


def sign_detect():
    global sign, num_sign, frame, sign_frame
    while True:
        sign, sign_frame = sign_detection(frame)
        filename = f"./images_sign/frame{num_sign}.jpg"
        cv2.imwrite(filename, sign_frame)
        print(f'[sign] {num_sign}th: {sign}')
        num_sign += 1


def check_sign():
    global left, right
    if signal == 'stop':
        left = 10
        right = 10
        return True
    elif signal == 'left':
        left = 21
        right = 21
        return True
    elif signal == 'right':
        left = 22
        right = 22
        return True
    elif signal == 'go':
        left = BASE
        right = BASE
        return True
    else:
        return False


def get_speed(slope):
    global signal, sign, line_count, BASE, SIGN_ADD

    left = BASE
    right = BASE

    if check_sign():
        pass
    else:  # 신호등 인식 못했을 때 (신호등 없을 때)
        if sign == '50':
            SIGN_ADD = 20
        elif sign == '30':
            SIGN_ADD = 0

        if line_count == 1:
            slope = slope * 20
            print(f'slope * 20 = {slope}')

        slope *= 20
        left = int(BASE - slope)
        right = int(BASE + slope)

        MIN = 35
        # MAX = int(60 + abs(slope)*0.01)
        MAX = int(60 + 0.05 * pow(abs(slope * 0.05), 1.9))

        if left < MIN:
            left = MIN
        elif left > MAX:
            left = MAX
        if right < MIN:
            right = MIN
        elif right > MAX:
            right = MAX

        left += SIGN_ADD
        right += SIGN_ADD + 1   # 오른쪽 바퀴의 모터 출력이 낮아서 맞춰줌

    return left, right


def init():         # get first frame to start other threads
    global frame
    length = recvall(client_socket, 16)
    recv_stringData = recvall(client_socket, int(length))
    recv_data = np.fromstring(recv_stringData, dtype='uint8')
    frame = cv2.imdecode(recv_data, cv2.IMREAD_COLOR)

    send_data = np.array([0, 0])
    send_stringData = send_data.tostring()
    client_socket.send(send_stringData)
    time.sleep(0.1)


def main():
    global frame

    init()
    t1 = threading.Thread(target=signal_detect)
    t2 = threading.Thread(target=sign_detect)
    t3 = threading.Thread(target=line_detect)

    t1.setDaemon(True)
    t2.setDaemon(True)
    t3.setDaemon(True)

    t1.start()
    t2.start()
    t3.start()

    num = 0
    while True:
        try:
            print(f"------------------------------{num}th frame------------------------------------")
            length = recvall(client_socket, 16)
            recv_stringData = recvall(client_socket, int(length))
            recv_data = np.fromstring(recv_stringData, dtype='uint8')
            frame = cv2.imdecode(recv_data, cv2.IMREAD_COLOR)

            # time.sleep(0.03)
            cv2.imshow("line detect", lined_frame)
            cv2.imshow("sign detect", sign_frame)
            cv2.moveWindow("sign detect", 641, 0)
            cv2.imshow("signal detect", signal_frame)
            cv2.moveWindow("signal detect", 0, 500)
            cv2.waitKey(1) & 0xFF

            send_data = np.array([left, right])              # left, right 값 RC카에 전송
            send_stringData = send_data.tostring()
            client_socket.send(send_stringData)
            num += 1

        except Exception as e:
            print("\033[95m Error: ", e, '\033[0m')
            send_data = np.array([0, 0])
            send_stringData = send_data.tostring()
            client_socket.send(send_stringData)
            time.sleep(0.1)
            continue


try:
    main()
except KeyboardInterrupt:
    server_socket.close()
    client_socket.close()
    cv2.destroyAllWindows()
    print("terminated...")
    exit(0)
