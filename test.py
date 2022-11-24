from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import math
import numpy as np


PI = 3.141592
POSITION_Y = 151
FRAME_WIDTH = 320
# HSV Color Condigion (Yellow)
Y_H_LOW = 20
Y_H_HIGH = 70
Y_S_LOW = 60
Y_S_HIGH = 250
Y_V_LOW = 30
Y_V_HIGH = 255
# HSV Color Condition (Red)
R_H_LOW = 0
R_H_HIGH = 60
R_S_LOW = 10
R_S_HIGH = 255
R_V_LOW = 10
R_V_HIGH = 255
# HSV Color Condition (Green)
G_H_LOW = 60
G_H_HIGH = 160
G_S_LOW = 0
G_S_HIGH = 255
G_V_LOW = 0
G_V_HIGH = 255
# HSV Color Condition (White)
W_H_LOW = 0
W_H_HIGH = 360
W_S_LOW = 0
W_S_HIGH = 45
W_V_LOW = 230
W_V_HIGH = 255

H = 480
W = 640

camera = PiCamera()
camera.resolution = (W, H)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(W, H))

time.sleep(0.1)

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array

    # 영상 블러, 에지 부각
    # hsv_img = np.zeros((H, W), image.dtype)
    # gray_img = np.zeros((H, W), image.dtype)
    # filtered_img = np.zeros((H, W), image.dtype)
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    gray_img = cv2.cvtColor(hsv_img, cv2.COLOR_BGR2GRAY)

    sigmaColor = 10.0
    sigmaSpace = 10.0
    filtered_img = cv2.bilateralFilter(gray_img, -1, sigmaColor, sigmaSpace)

    # 원 검출
    circles = cv2.HoughCircles(filtered_img, cv2.HOUGH_GRADIENT, 5, 100,
                               param1=50, param2=300, minRadius= 50, maxRadius=60)

    if (circles is not None):

        circles = circles[0]

        for i in range(len(circles)):
            print(circles[i][0]) # 각 원 순서대로 중심점 출력

        # 검출된 원 내부 색상정보
        for i in range(len(circles)):
            center = [round(circles[i][0]), round(circles[i][1])]
            radius = round(circles[i][2])
            print("center: ", center)

            x = center[0]
            y = center[1]
            # indexoutofrange 오류 해결
            if (y == 480 or x == 640):
                y = 479
                x = 639
            print(f"x: {x}, y: {y}")
            B = image[y][x][0]
            G = image[y][x][1]
            R = image[y][x][2]
            print(f"R: {R}, G: {G}, B: {B}")

            if (R-B > 20 and R-G > 20 and R > 100):
                print("Red Light!! Stop!")
                cv2.line(image, (x, y), (x, y), (255, 0, 0), 5)  # 빨간원으로 인식했을때 중점찍기
            if (G-R > 20 and G-B > 20 and G > 100):
                print("Detected Green Light")
                CenterX = center[0]
                CenterY = center[1]
                if (CenterY == 480 or CenterX == 640):
                    CenterY = 479
                    CenterX = 639
                Cradius = radius
                Width = 2*Cradius
                Height = 2*Cradius
                TotalPixel = math.floor(PI*Cradius*Cradius)
                green_cnt_r = 0
                green_cnt_l = 0
                cv2.line(image, (x, y), (x, y), (0, 0, 255), 5)  # 초록원으로 인식했을때 중점찍기

                for k in range(CenterX-Width, CenterX+Width+1):
                    for j in range(CenterY-Height, CenterY+Height+1):
                        blue_data = image[j, k, 0]
                        green_data = image[j, k, 1]
                        red_data = image[j, k, 2]

                        if (green_data-blue_data > 20 and green_data-red_data > 20 and green_data > 100):
                            if (k <= CenterX): green_cnt_l += 1
                            else: green_cnt_r += 1

                print(f'green_cnt: {green_cnt_r + green_cnt_l} Total Pixel: {TotalPixel}')
                if (TotalPixel*0.6 < green_cnt_r + green_cnt_l):
                    if (green_cnt_r > green_cnt_l): print("Go Right ->")
                    else: print("Go Left <-")

            else: print("stay stop!")
            cv2.circle(image, (x, y), radius, (255, 0, 0), 5)  # 원그리기

    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)  # clear stream

    if key == ord("q"):
        break