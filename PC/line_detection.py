import cv2
import numpy as np
import copy

global slopes
slopes = []

def canny_edge(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary_image = cv2.threshold(blur, 200, 255, cv2.THRESH_BINARY)
    # _, binary_image = cv2.threshold(blur, -1, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    canny_image = cv2.Canny(binary_image, 50, 150)
    return canny_image


def get_roi(img, x1, y1, x2, y2, x3, y3, x4, y4):   # (x1,y1): 좌하단, (x2, y2): 좌상단, (x3, y3): 우상단, (x4, y4): 우하단
    # 직사각형 모양 ROI 설정
    rectangle = np.array([[(x1, y1), (x2, y2), (x3, y3), (x4, y4)]])
    # creating black image same as that of input image
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, rectangle, 255)
    masked_image = cv2.bitwise_and(img, mask)   # ROI 대로 크롭된 원본 이미지
    return masked_image


def get_lines(img):
    lines = cv2.HoughLinesP(img, 2, np.pi / 180, 80, np.array([]), minLineLength=40, maxLineGap=5)
    return lines


# display lines over a image
def display_lines(img, lines):
    if lines is not None:
        if (type(lines) is list):
            print("One line detected!")
            lines = np.array([[lines]])
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)  # converting to 1d array []
            cv2.line(img, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 10)
    return img


def get_linecoordinates_from_parameters(img, line_parameters):
    slope = line_parameters[0]
    intercept = line_parameters[1]
    # m : 기울기, c : y절편
    # y = mx + c , x = (y-c)/m
    y1 = img.shape[0]   # since line will always start from bottom of image
    y2 = 250
    x1 = float((y1 - intercept) / slope)
    x2 = float((y2 - intercept) / slope)

    if (x1 < 0):
        x1 = 0
        y1 = intercept
    elif (x1 > 637):
        x1 = 637
        y1 = 637 * slope + intercept
    if (x2 < 0):
        x2 = 0
        y2 = intercept
    elif (x2 > 637):
        x2 = 637
        y2 = 637 * slope + intercept
    return np.array([x1, y1, x2, y2])

def get_smooth_lines(img, lines):
    left_fit = []  # will hold m,c parameters for left side lines
    right_fit = []  # will hold m,c parameters for right side lines

    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)

        # numpy.polyfit(x좌표들, y좌표들, 방정식의 차수, rcond=None, full=False, w=None, cov=False)
        if x1 == x2:
            x1 += 1
        parameters = np.polyfit((x1, x2), (y1, y2), 1)

        # 기울기
        slope = parameters[0]
        # y절편
        intercept = parameters[1]

        # 기울기가 음수면 왼쪽 차선, 양수면 오른쪽 차선
        if abs(slope) < 0.1:
            pass
        elif slope < 0:
            left_fit.append([parameters[0], intercept])
        else:
            right_fit.append([parameters[0], intercept])

    # 직선들의 평균을 찾아 하나의 직선으로 만들기
    # 이것 말고도 중점에 가까운 직선을 구하는 방법도 있음. 뭐가 더 좋을지는 주행 해봐야 알 것 같다.
    if (len(left_fit) == 0):            # 오른쪽 차선만 인식된 경우
        right_fit_average = np.average(right_fit, axis=0)
        right_line = get_linecoordinates_from_parameters(img, right_fit_average)
        return list(right_line)
    elif (len(right_fit) == 0):         # 왼쪽 차선만 인식된 경우
        left_fit_average = np.average(left_fit, axis=0)
        left_line = get_linecoordinates_from_parameters(img, left_fit_average)
        return list(left_line)

    # 둘 다 인식된 경우
    left_fit_average = np.average(left_fit, axis=0)
    right_fit_average = np.average(right_fit, axis=0)

    # 선분으로 그려주기 위해 좌표 찾기
    left_line = get_linecoordinates_from_parameters(img, left_fit_average)
    right_line = get_linecoordinates_from_parameters(img, right_fit_average)
    return np.array([left_line, right_line])



# 소실점 구하기
def find_point(img, lines):
    if (type(lines) is list):
        # 왼쪽 | 오른쪽 중 하나만 들어왔을 때
        if lines[1] == lines[3]:
            lines[1] += 1
        parameters = np.polyfit((lines[1], lines[3]), (lines[0], lines[2]), 1)
        return np.array([[0, 0, 0, 0]]), parameters[0], 1

    if lines[0][2] == lines[0][0]:
        lines[0][2] += 1
    if lines[1][2] == lines[1][0]:
        lines[1][2] += 1

    m = np.array([(lines[0][3]-lines[0][1]) / (lines[0][2]-lines[0][0]), (lines[1][3]-lines[1][1]) / (lines[1][2]-lines[1][0])])    # 왼쪽 기울기, 오른쪽 기울기

    # 왼쪽 오른쪽 직선의 중점
    x_mid_point = (lines[0][0]+lines[1][0])/2   # (left line, right line의 중점, 480)
    y_mid_point = (lines[0][1]+lines[1][1])/2

    cl = lines[0][1] - m[0] * lines[0][0]
    cr = lines[1][1] - m[1] * lines[1][0]
    # y = m[0] * x + cl, y = m[1] * x + cr

    # 소실점 좌표
    x_vanish = (cl-cr)/(m[1]-m[0])
    y_vanish = m[0] * x_vanish + cl

    parameters = np.polyfit((x_vanish, x_mid_point), (y_vanish, y_mid_point), 1)
    parameters_swap = np.polyfit((y_vanish, y_mid_point), (x_vanish, x_mid_point), 1)
    slope = parameters[0]

    slopes.append(parameters_swap[0])

    intercept = parameters[1]
    # m : slope, c : intercept
    # y = mx + c , x = (y-c)/m
    y1 = img.shape[0]  # since line will always start from bottom of image
    y2 = float(y1 * (3.4 / 5))  # some random point at 3.4/5
    x1 = float((y1 - intercept) / slope)
    x2 = float((y2 - intercept) / slope)

    if (x1 < 0):
        x1 = 0
        y1 = intercept
    elif (x1 > 637):
        x1 = 637
        y1 = 637 * slope + intercept
    if (x2 < 0):
        x2 = 0
        y2 = intercept
    elif (x2 > 637):
        x2 = 637
        y2 = 637 * slope + intercept

    return np.array([[x1, y1, x2, y2]]), parameters_swap[0], 2


def line_detection(frame):
    image = copy.deepcopy(frame)
    edged_image = canny_edge(image)

    roi_image = get_roi(edged_image, 0, 479, 0, 250, 637, 250, 637, 479)
    points = np.array([[0, 479], [0, 250], [637, 250], [637, 479]])
    cv2.polylines(image, np.int32([points]), True, (0, 255, 255), thickness=2)

    lines = get_lines(roi_image)

    smooth_lines = get_smooth_lines(image, lines)
    image_with_smooth_lines = display_lines(image, smooth_lines)
    vanishpoint_line, slope, line_num = find_point(image, smooth_lines)
    image_with_vanishpoint_line = display_lines(image_with_smooth_lines, vanishpoint_line)

    for i in lines:
        cv2.line(image_with_vanishpoint_line, (i[0][0], i[0][1]), (i[0][2], i[0][3]), (0, 0, 255), 2)

    return slope, image_with_vanishpoint_line, line_num

