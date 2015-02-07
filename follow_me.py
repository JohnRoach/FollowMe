import cv
import sys
import ksr10


def find_red_square(image):
    size = cv.GetSize(image)

    # prepare memory
    square = cv.CreateImage(size, 8, 1)
    red = cv.CreateImage(size, 8, 1)
    hsv = cv.CreateImage(size, 8, 3)
    sat = cv.CreateImage(size, 8, 1)

    # split image into hsv, grab the sat
    cv.CvtColor(image, hsv, cv.CV_BGR2HSV)
    cv.Split(hsv, None, sat, None, None)

    # split image into rgb
    cv.Split(image, None, None, red, None)

    # find the square by looking for red, with high saturation
    cv.Threshold(red, red, 128, 255, cv.CV_THRESH_BINARY)
    cv.Threshold(sat, sat, 128, 255, cv.CV_THRESH_BINARY)

    # AND the two thresholds, finding the square
    cv.Mul(red, sat, square)

    # remove noise, highlighting the square
    cv.Erode(square, square, iterations=5)
    cv.Dilate(square, square, iterations=5)

    storage = cv.CreateMemStorage(0)
    obj = cv.FindContours(square, storage, cv.CV_RETR_CCOMP,
                          cv.CV_CHAIN_APPROX_SIMPLE)
    cv.ShowImage('A', square)

    if not obj:
        return 0, 0, 0, 0
    else:
        return cv.BoundingRect(obj)


points = []
capture = cv.CaptureFromCAM(0)
if not capture:
    print "Error opening capture device"
    sys.exit(1)

cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_WIDTH, 640)
cv.SetCaptureProperty(capture, cv.CV_CAP_PROP_FRAME_HEIGHT, 480)
# create object
ksr = ksr10.ksr10_class()
# turn on lights
ksr.lights()

while 1:

    original = cv.QueryFrame(capture)
    square_rect = find_red_square(original)
    x, y, width, height = square_rect
    print square_rect
    x1 = x / 6
    y1 = y / 4
    if (0 < x1) and (x1 < 50):
        ksr.move("base", "left")
    elif (50 < x1) and (x1 < 100):
        ksr.move("base", "right")
    if (0 < y1) and (y1 < 50):
        ksr.move("elbow", "up")
    elif (50 < y1) and (y1 < 100):
        ksr.move("elbow", "down")
    middle = (square_rect[0] + (square_rect[2] / 2), square_rect[1] +
              (square_rect[3] / 2))
    if not points:
        points.append(middle)
    else:
        if abs(points[-1][0] - middle[0]) > 5 and \
                        abs(points[-1][1] - middle[1]) > 10:
            points.append(middle)

        cv.Rectangle(original,
                     (square_rect[0], square_rect[1]),
                     (square_rect[0] + square_rect[2],
                      square_rect[1] + square_rect[3]),
                     (255, 0, 0), 1, 8, 0)

    for point in points:
        cv.Circle(original, point, 1, (0, 0, 255), -1, 8, 0)

    cv.ShowImage('Analysed', original)
    k = cv.WaitKey(33)
