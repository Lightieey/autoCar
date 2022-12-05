from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import YB_Pcb_Car
import light_detect
import math
from line_detection import line_detection
from light_detect import light_detection

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32   # 높여서 안끊기게 해보기 -> 연산처리 속도 보기
rawCapture = PiRGBArray(camera, size=(640, 480))

time.sleep(0.1)   # warm up

# 영상 저장ㅎ
# fourcc = cv2.VideoWriter_fourcc('A', 'V', 'C', '1')
# out = cv2.VideoWriter('output.avi', fourcc, 1.0, (640, 480))

num = 0
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # 창 따로 뜨는지 확인
    try:
        slope, lined_frame = line_detection(frame)

        num += 1
        filename = f"frame{num}.jpg"
        cv2.imwrite(filename, lined_frame)

        signal = light_detection(lined_frame)
        print(signal)

        # 모터 제어--
        car = YB_Pcb_Car.YB_Pcb_Car()

        car.Car_Run(int(30 + slope*10), int(30 - slope*10))
        # if (slope < 0 and slope > -10):
        #     car.Car_Run(30 + abs(math.ceil(slope))*3, 30 - abs(math.ceil(slope))*3)
        #     print("2) slope:", slope, "left:", 30 + abs(math.ceil(slope))*3, "right:", 30 - abs(math.ceil(slope))*3)
        # elif (slope > 0 and slope < 10):
        #     car.Car_Run(30 - abs(math.ceil(slope))*3, 30 + abs(math.ceil(slope))*3)
        #     print("3) slope:", slope, "left:", 30 - abs(math.ceil(slope))*3, "right:", 30 + abs(math.ceil(slope))*3)
        # else:
        #     car.Car_Run(30, 30)
        #     print("1) slope: ", slope)
        time.sleep(0.1)

        # car.Car_Stop()
        # cv2.waitKey(0)

    except Exception as e:
        print(e)
        car.Car_Stop()
        # out.release()
        break
    except KeyboardInterrupt:
        car.Car_Stop()
        # cv2.destroyAllWindows()
        # out.release()
        break
    finally:
        key = cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)





