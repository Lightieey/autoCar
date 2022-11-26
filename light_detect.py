from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import math
from line_detection import get_roi

PI = 3.141592
H = 480
W = 640


def init():
    global camera
    camera = PiCamera()
    camera.resolution = (W, H)
    camera.framerate = 32
    global rawCapture
    rawCapture = PiRGBArray(camera, size=(W, H))

    time.sleep(0.1)


def light_detection(frame):
    #image = frame.array
    image = frame

    roi_image = get_roi(image, 100, 150, 100, 0, 540, 0, 540, 150)  # roi 설정
    cv2.rectangle(image, (100, 150), (540, 0), color=(0, 0, 255))
    # 영상 블러, 에지 부각
    # hsv_img = np.zeros((H, W), image.dtype)
    # gray_img = np.zeros((H, W), image.dtype)
    # filtered_img = np.zeros((H, W), image.dtype)
    hsv_img = cv2.cvtColor(roi_image, cv2.COLOR_BGR2HSV)
    gray_img = cv2.cvtColor(hsv_img, cv2.COLOR_BGR2GRAY)


    sigmaColor = 10.0
    sigmaSpace = 10.0
    filtered_img = cv2.bilateralFilter(gray_img, -1, sigmaColor, sigmaSpace)

    # 원 검출
    circles = cv2.HoughCircles(filtered_img, cv2.HOUGH_GRADIENT, 5, 100,
                               param1=50, param2=300, minRadius= 30, maxRadius=50)

    result = "Not found"
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
                print(" !Red Light! ")
                cv2.line(image, (x, y), (x, y), (255, 0, 0), 5)  # 빨간원으로 인식했을때 중점찍기
                result = "stop"

            elif (G-R > 20 and G-B > 20 and G > 100):
                print(" !Green Light! ")
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
                    if (k == 640):
                        k = 639
                    for j in range(CenterY-Height, CenterY+Height+1):
                        if (j == 480):
                            j = 479
                        blue_data = image[j, k, 0]
                        green_data = image[j, k, 1]
                        red_data = image[j, k, 2]

                        if (green_data-blue_data > 20 and green_data-red_data > 20 and green_data > 100):
                            if (k <= CenterX): green_cnt_l += 1
                            else: green_cnt_r += 1

                print(f'green_cnt: {green_cnt_r + green_cnt_l} Total Pixel: {TotalPixel}')
                if (TotalPixel*0.6 > green_cnt_r + green_cnt_l):
                    if (green_cnt_r > green_cnt_l):
                        print("! Go Right -> !")
                        result = "right"
                    else:
                        print("! Go Left <- !")
                        result = "left"
                result = "go"

            else:
                print("stay stop!")
                result = "stop"
            cv2.circle(image, (x, y), radius, (255, 0, 0), 5)  # 원그리기

    cv2.imshow("Frame", image)
    return result





if __name__ == '__main__':
    init()
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        res = light_detection(frame)
        print(res)
        cv2.waitKey(1) & 0xFF
        rawCapture.truncate(0)  # clear stream



