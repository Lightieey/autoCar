import cv2
import math
from line_detection import get_roi
import copy

PI = 3.141592
H = 480
W = 640


def light_detection(frame):
    image = copy.deepcopy(frame)

    roi_image = get_roi(image, 0, 150, 0, 0, 420, 0, 420, 150)  # roi 설정
    cv2.rectangle(image, (0, 150), (420, 0), color=(255, 0, 0), thickness=2)

    hsv_img = cv2.cvtColor(roi_image, cv2.COLOR_BGR2HSV)
    gray_img = cv2.cvtColor(hsv_img, cv2.COLOR_BGR2GRAY)


    sigmaColor = 10.0
    sigmaSpace = 10.0
    filtered_img = cv2.bilateralFilter(gray_img, -1, sigmaColor, sigmaSpace)

    # 원 검출
    circles = cv2.HoughCircles(filtered_img, cv2.HOUGH_GRADIENT, 5, 100,
                               param1=100, param2=250, minRadius=1, maxRadius=60)

    result = "Not found"
    if (circles is not None):

        circles = circles[0]

        for i in range(len(circles)):
            print(circles[i][0])    # 각 원 순서대로 중심점 출력

        # 검출된 원 내부 색상 정보
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
                cv2.line(image, (x, y), (x, y), (255, 0, 0), 5)  # 빨간원으로 인식했을때 중점찍기 (파란색)
                result = "stop"

            elif (G-R > 20 and G-B > 20 and G > 100):
                print(" !Green Light! ")
                CenterX = center[0]
                CenterY = center[1]
                if (CenterY == 480 or CenterX == 640):
                    CenterY = 479
                    CenterX = 639
                Cradius = radius
                TotalPixel = math.floor(PI*Cradius*Cradius)
                green_cnt_r = 0
                green_cnt_l = 0
                cv2.line(image, (x, y), (x, y), (0, 0, 255), 5)  # 초록원으로 인식했을때 중점찍기 (빨간색)

                for k in range(CenterX-Cradius, CenterX+Cradius+1):
                    if (k == 640):
                        k = 639
                    for j in range(CenterY-Cradius, CenterY+Cradius+1):
                        if (j == 480):
                            j = 479
                        blue_data = image[j, k, 0]
                        green_data = image[j, k, 1]
                        red_data = image[j, k, 2]

                        if green_data-blue_data > 20 and green_data-red_data > 20 and green_data > 100:
                            if (k <= CenterX): green_cnt_l += 1
                            else: green_cnt_r += 1

                print(f'Total Pixel: {TotalPixel}, left green cnt: {green_cnt_l}, right green cnt: {green_cnt_r} ')
                if (TotalPixel*0.6 > green_cnt_r + green_cnt_l):
                    if (green_cnt_r > green_cnt_l):
                        cv2.line(image, (x, y), (x, y), (0, 0, 0), 5)  # 우회전으로 인식했을때 중점찍기 (검정색)
                        print("! Go Right -> !")
                        result = "right"
                    else:
                        print("! Go Left <- !")
                        cv2.line(image, (x, y), (x, y), (255, 255, 255), 5)  # 좌회전으로 인식했을때 중점찍기 (하얀색)
                        result = "left"
                else:
                    result = "go"

            else:
                print("stay stop!")
                result = "stop"
            cv2.circle(image, (x, y), radius, (255, 0, 0), 5)  # 원그리기

    return result, image




