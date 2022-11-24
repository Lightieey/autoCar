from picamera.array import PiRGBArray
from picamera import PiCamera
import picamera
import time
import cv2
import numpy as np

global slopes
slopes = []

def canny_edge(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    canny_image = cv2.Canny(blur, 50, 150)
    return canny_image


def get_roi(img, x1, y1, x2, y2, x3, y3, x4, y4):   # (x1,y1): 좌하단, (x2, y2): 좌상단, (x3, y3): 우상단, (x4, y4): 우하단
    # 직사각형 모양 ROI 설정
    rectangle = np.array([[(x1, y1), (x2, y2), (x3, y3), (x4, y4)]])    # 입력 영상에 따라 수정 필요 (좌표값의 의미는 알아보기)
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
    #lines = cv2.HoughLines(img, 0.8, np.pi / 180, 100)
    #print("HoughLines: ", lines)
    return lines


# display lines over a image
def display_lines(img, lines):
    if lines is not None:
        if (type(lines) is list):
            print("lines is list")
            lines = np.array([[lines]])
        for line in lines:
            print("line: ", line)
            # print(line) --output like [[704 418 927 641]] this is 2d array representing [[x1,y1,x2,y2]] for each line
            x1, y1, x2, y2 = line.reshape(4)  # converting to 1d array []
            # draw line over image --(255,0,0) tells we want to draw blue line (b,g,r) values 10 is line thickness
            cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 10)
    return img


def get_linecoordinates_from_parameters(img, line_parameters):
    slope = line_parameters[0]
    intercept = line_parameters[1]
    # m : 기울기, c : y절편
    # y = mx + c , x = (y-c)/m
    y1 = 480  # since line will always start from bottom of image
    y2 = float(y1 * (3.4 / 5))  # some random point at 3/5
    x1 = float((y1 - intercept) / slope)
    x2 = float((y2 - intercept) / slope)
    return np.array([x1, y1, x2, y2])


def get_smooth_lines(img, lines):
    left_fit = []  # will hold m,c parameters for left side lines
    right_fit = []  # will hold m,c parameters for right side lines

    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        # numpy.polyfit(x좌표들, y좌표들, 방정식의 차수, rcond=None, full=False, w=None, cov=False)
        parameters = np.polyfit((x1, x2), (y1, y2), 1)
        # 기울기
        slope = parameters[0]
        # y절편
        intercept = parameters[1]

        # 기울기가 음수면 왼쪽 차선, 양수면 오른쪽 차선
        if slope < 0:
            left_fit.append([slope, intercept])
        else:
            right_fit.append([slope, intercept])

    # 직선들의 평균을 찾아 하나의 직선으로 만들기 # 이것 말고도 중점에 가까운 직선을 구하는 방법도 있음. 뭐가 더 좋을지는 주행 해봐야 알 것 같다.
    # axis=0으로 지정하면 row를 기준으로 연산 / axis=1으로 지정하면 column을 기준으로 연산
    if (len(left_fit) == 0):
        right_fit_average = np.average(right_fit, axis=0)
        return list(right_fit_average)
    elif (len(right_fit) == 0):
        left_fit_average = np.average(left_fit, axis=0)
        return list(left_fit_average)
        # 모터 제어 - 그냥 후진


    left_fit_average = np.average(left_fit, axis=0)
    right_fit_average = np.average(right_fit, axis=0)

    # now we have got m,c parameters for left and right line, we need to know x1,y1 x2,y2 parameters
    # 선분으로 그려주기 위해 좌표 찾기
    left_line = get_linecoordinates_from_parameters(img, left_fit_average)
    right_line = get_linecoordinates_from_parameters(img, right_fit_average)
    print("left, right")
    print(np.array([left_line, right_line]))
    return np.array([left_line, right_line])



# 소실점 구하기
def find_point(img, lines):
    if (type(lines) is list):
        return np.array([[0, 0, 0, 0]]), lines[0][0]
    m = np.array([(lines[0][3]-lines[0][1])/(lines[0][2]-lines[0][0]), (lines[1][3]-lines[1][1])/(lines[1][2]-lines[1][0])])# 왼쪽 기울기, 오른쪽 기울기
    # lines = (L[x1, y1, x2, y2] , R[x1,y1,x2,y2])

    # 왼쪽 오른쪽 직선의 중점
    x_mid_point = (lines[0][0]+lines[1][0])/2   # (left line, right line의 중점, 480)
    # y_mid_point = 480
    y_mid_point = (lines[0][1]+lines[1][1])/2

    cl = lines[0][1] - m[0] * lines[0][0]
    cr = lines[1][1] - m[1] * lines[1][0]
    # y = m[0] * x + cl, y = m[1] * x + cr

    # 소실점 좌표
    x_vanish = (cl-cr)/(m[1]-m[0])
    y_vanish = m[0] * x_vanish + cl

    parameters = np.polyfit((x_vanish, x_mid_point), (y_vanish, y_mid_point), 1)
    slope = parameters[0]
    print("slope: ", slope)
    slopes.append(slope)
    intercept = parameters[1]
    # m : slope, c : intercept
    # y = mx + c , x = (y-c)/m
    y1 = img.shape[0]  # since line will always start from bottom of image
    y2 = int(y1 * (3.4 / 5))  # some random point at 3/5
    x1 = int((y1 - intercept) / slope)
    x2 = int((y2 - intercept) / slope)

    return np.array([[x1, y1, x2, y2]]), slope


def line_detection(frame):
    image = frame.array
    edged_image = canny_edge(image)
    roi_image = get_roi(edged_image, 0, 480, 120, 300, 520, 300, 640, 480)


    lines = get_lines(roi_image)
    # for i in lines:
    #
    #     cv2.line(image, (i[0][0], i[0][1]), (i[0][2], i[0][3]), (0, 0, 255), 2)

    # cv2.imshow("Output", image)
    # cv2.waitKey(0)

    # image_with_lines = display_lines(image, lines)
    smooth_lines = get_smooth_lines(image, lines)
    image_with_smooth_lines = display_lines(image, smooth_lines)
    # cv2.imshow("Output", image_with_smooth_lines)
    # cv2.waitKey(0)

    vanishpoint_line, slope = find_point(image, smooth_lines)
    image_with_vanishpoint_line = display_lines(image_with_smooth_lines, vanishpoint_line)

    # cv2.imshow("Output", image_with_vanishpoint_line)

    return slope, image_with_vanishpoint_line




def init():
    # main code
    global camera
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32

    global rawCapture
    rawCapture = PiRGBArray(camera, size=(640, 480))

    # allow the camera to warm up
    time.sleep(0.1)


if __name__ == '__main__':
    init()
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        try:
            line_detection(frame)

        # except Exception as e:
        #     print(e)
        finally:
            key = cv2.waitKey(1) & 0xFF
            rawCapture.truncate(0)


