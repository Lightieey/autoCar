from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np


def canny_edge(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    canny_image = cv2.Canny(blur, 50, 150)
    return canny_image


def get_roi(img):
    height = img.shape[0]
    # 직사각형 모양 ROI 설정
    rectangle = np.array([[(0, height), (120, 300), (520, 300), (640, height)]])    # 입력 영상에 따라 수정 필요 (좌표값의 의미는 알아봐야함)
    # creating black image same as that of input image
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, rectangle, 255)
    masked_image = cv2.bitwise_and(img, mask)   # ROI 대로 크롭된 원본 이미지
    return masked_image


def get_lines(img):
    # lines=cv2.HoughLinesP(image,bin_size,precision,threshold,dummy 2d array--no use,minLineLength,maxLineGap)
    # lets take bin size to be 2 pixels
    # lets take precision to be 1 degree= pi/180 radians
    # threshold is the votes that a bin should have to be accepted to draw a line
    # minLineLength --the minimum length in pixels a line should have to be accepted.
    # maxLineGap --the max gap between 2 broken line which we allow for 2 lines to be connected together.
    lines = cv2.HoughLinesP(img, 2, np.pi / 180, 100, np.array([]), minLineLength=40, maxLineGap=5)
    return lines


# display lines over a image
def display_lines(img, lines):
    if lines is not None:
        for line in lines:
            # print(line) --output like [[704 418 927 641]] this is 2d array representing [[x1,y1,x2,y2]] for each line
            x1, y1, x2, y2 = line.reshape(4)  # converting to 1d array []

            # draw line over black image --(255,0,0) tells we want to draw blue line (b,g,r) values 10 is line thickness
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 10)
    return img


def getLineCoordinatesFromParameters(img, line_parameters):
    slope = line_parameters[0]
    intercept = line_parameters[1]
    # m : slope, c : intercept
    # y = mx + c , x = (y-c)/m
    y1 = img.shape[0]  # since line will always start from bottom of image
    y2 = int(y1 * (3.4 / 5))  # some random point at 3/5
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)
    return np.array([x1, y1, x2, y2])

def getSmoothLines(img, lines):
    left_fit = []  # will hold m,c parameters for left side lines
    right_fit = []  # will hold m,c parameters for right side lines

    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        # polyfit gives slope(m) and intercept(c) values from input points
        # last parameter 1 is for linear..so it will give linear parameters m,c
        # numpy.polyfit(x좌표들, y좌표들, deg 차수, rcond=None, full=False, w=None, cov=False)
        parameters = np.polyfit((x1, x2), (y1, y2), 1)
        # 기울기
        slope = parameters[0]
        # y절편
        intercept = parameters[1]

        # 기울기가 음수면 왼쪽 차선, 양수면 오른쪽 차선
        if slope < 0:
            left_fit.append((slope, intercept))
        else:
            right_fit.append((slope, intercept))

    # 직선들의 평균을 찾아 하나의 직선으로 만들기 # 이것 말고도 중점에 가까운 직선을 구하는 방법도 있음. 뭐가 더 좋을지는 주행 해봐야 알 것 같다.
    # take averages of all intercepts and slopes separately and get 1 single value for slope,intercept
    # axis=0 means vertically...see its always (row,column)...so row is always 0 position.
    # so axis 0 means over row(vertically)
    # axis=0으로 지정하면 row를 기준으로 연산
    # axis=1으로 지정하면 column을 기준으로 연산
    left_fit_average = np.average(left_fit, axis=0)
    right_fit_average = np.average(right_fit, axis=0)

    # now we have got m,c parameters for left and right line, we need to know x1,y1 x2,y2 parameters
    # 선분으로 그려주기
    print("left")
    print(left_fit_average)
    print("right")
    print(right_fit_average)
    left_line = getLineCoordinatesFromParameters(img, left_fit_average)
    right_line = getLineCoordinatesFromParameters(img, right_fit_average)
    return np.array([left_line, right_line])


# 소실점 & 각도 구하는 함수 작성 필요


# main code


camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640,480))

# allow the camera to warmup
time.sleep(0.1)


for frame in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
    image = frame.array

    edged_image = canny_edge(image)  # Step 1

    roi_image = get_roi(edged_image)  # Step 2

    lines = get_lines(roi_image)  # Step 3
    #image_with_lines = display_lines(image, lines)

    smooth_lines = getSmoothLines(image, lines)  # Step 5
    image_with_smooth_lines = display_lines(image, smooth_lines)  # Step 4

    cv2.imshow("Output", image_with_smooth_lines)
    #cv2.waitKey(0)

    rawCapture.truncate(0)

    # Press Q to quit
    key = cv2.waitKey(1) & 0xff
    if key == ord('q'):
        break




