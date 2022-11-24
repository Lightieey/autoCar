from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import YB_Pcb_Car
import light_detect
from line_detection import line_detection
from light_detect import light_detection

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32   # 높여서 안끊기게 해보기 -> 연산처리 속도 보기
rawCapture = PiRGBArray(camera, size=(640, 480))

time.sleep(0.1)     # warm up

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # 창 따로 뜨는지 확인
    try:
        slope, lined_frame = line_detection(frame)
        signal = light_detection(lined_frame)
        print(signal)

        # 모터 제어
        car = YB_Pcb_Car.YB_Pcb_Car()

        if (slope < 0 and slope > -10):
            car.Car_Run(30 + abs(slope), 30 - abs(slope))
            print("2) slope: ", slope)
        elif (slope > 0 and slope < 10):
            car.Car_Run(30 - abs(slope), 30 + abs(slope))
            print("3) slope: ", slope)
        else:
            car.Car_Run(30, 30)
            print("1) slope: ", slope)
        time.sleep(0.1)

    # except Exception as e:
    #     print(e)
        # car.Car_Stop()
    except KeyboardInterrupt:
        car.Car_Stop()
    finally:
        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)


