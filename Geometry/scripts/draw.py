
import math

import cv2

from scripts.globalParameters import Unit
FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SIZE = 0.4
WHITE = (255,255,255)

def drawVerticalROI(image, numVerticalROIs, color = WHITE):
    """
    Draws lines on input image demarcating the vertical ROIs
    :param image: Input image to draw lines on.
    :param numVerticalROIs: number of vertical ROIs to draw.
    :param color: color of line. Default is white
    :return: Edged image.
    """

    thickness   = 1
    frameHeight, frameWidth = image.shape[:2]
    ROIWidth = frameWidth // numVerticalROIs
    for x in range(ROIWidth, frameWidth, ROIWidth):
        text = 'ROI'+str(x+1)
        text_position = (x+ROIWidth//2, 20)
        cv2.line(image, (x, 0), (x, frameHeight), color, thickness)
        cv2.putText(image, text, text_position, FONT_FACE, FONT_SIZE, color, thickness, lineType=cv2.LINE_AA)

          
def drawHorizontalROI(image, numHorizontalROIs, color = WHITE):
    """
    Draws lines on input image demarcating the horizontal ROIs
    :param image: Input image to draw lines on.
    :param numHorizontalROIs: number of horizontal ROIs to draw.
    :param color: color of line. Default is white
    :return: Edged image.
    """
    thickness   = 1
    frameHeight, frameWidth = image.shape[:2]
    ROIWidth = frameHeight // numHorizontalROIs
    for x in range(ROIWidth, frameWidth, ROIWidth):
        cv2.line(image, (0, x), (frameWidth, x), color, thickness)
        text = 'ROI'+str(x+1)
        text_position = (20, x+ROIWidth//2)
        cv2.putText(image, text, text_position, FONT_FACE, FONT_SIZE, color, thickness, lineType=cv2.LINE_AA)


def drawVerticalLineandValue(image, z1, z2, color, value, unit = Unit.PIXELS):
    """
    Draws lines on input image indicating where the vertical length measurement is taken in each ROI
    :param image: Input image to draw lines on.
    :param z1: first point
    :param z2: second point
    :param value: length value associated with the measurement
    :param unit: unit of measurement to be printed. Default is Unit.PIXELS
    """
    thickness   = 1
    x1, y1 = z1
    x2, y2 = z2
    x = math.floor((x1 + x2) / 2)
    y = math.floor((y1 + y2) / 2)
    cv2.line(image, (x, y1), (x, y2), color, thickness)

    # Measurement value
    match unit:
        case Unit.PIXELS:
            units = ' px' 
        case Unit.MM:
            units = 'mm'
        case Unit.CM:
            units = 'cm'
        case _:
            units = ''
    text          = "{}".format(round(value, 1)) + units
    text_position = (x + 5, y)
    cv2.putText(image, text, text_position, FONT_FACE, FONT_SIZE, color, thickness, lineType=cv2.LINE_AA)
         
def drawHorizontalLineandValue(image, z1, z2, color, value, unit = Unit.PIXELS):
    """
    Draws lines on input image indicating where the horizontal length measurement is taken in each ROI
    :param image: Input image to draw lines on.
    :param z1: first point
    :param z2: second point
    :param value: length value associated with the measurement
    :param unit: unit of measurement to be printed. Default is Unit.PIXELS
    """
    thickness   = 1
    x1, y1 = z1
    x2, y2 = z2
    x = math.floor((x1 + x2) / 2)
    y = math.floor((y1 + y2) / 2)
    cv2.line(image, (x1, y), (x2, y), color, thickness)

    # Measurement value
    match unit:
        case Unit.PIXELS:
            units = ' px' 
        case Unit.MM:
            units = 'mm'
        case Unit.CM:
            units = 'cm'
        case _:
            units = 'units'
    text          = "{}".format(round(value, 1)) + units
    text_position = (x, y + 10)
    cv2.putText(image, text, text_position, FONT_FACE, FONT_SIZE, color, thickness, lineType=cv2.LINE_AA)
         