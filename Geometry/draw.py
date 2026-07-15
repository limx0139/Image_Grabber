
import math

import cv2
from matplotlib import image

from enums import Unit
FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SIZE = 0.4

def drawVerticalROI(image, color, numVerticalROIs):

      thickness   = 1
      num_rows, num_cols = image.shape[:2]
      width = num_cols // numVerticalROIs
      for x in range(width, num_cols, width):
          cv2.line(image, (x, 0), (x, num_rows), color, thickness)
          
def drawHorizontalROI(image, color, numHorizontalROIs):
    thickness   = 1
    num_rows, num_cols = image.shape[:2]
    width = num_rows // numHorizontalROIs
    for x in range(width, num_cols, width):
        cv2.line(image, (0, x), (num_cols, x), color, thickness)

def drawVerticalLineandValue(image, z1, z2, color, value, unit):
    thickness   = 1
    x1, y1 = z1
    x2, y2 = z2
    x = math.floor((x1 + x2) / 2)
    y = math.floor((y1 + y2) / 2)
    cv2.line(image, (x, y1), (x, y2), color, thickness)

    # Measurement value
    match unit:
        case Unit.PIXELS:
            units = ' pixels' 
        case Unit.MM:
            units = 'mm'
        case Unit.CM:
            units = 'cm'
        case _:
            units = ''
    text          = "{}".format(round(value, 1)) + units
    text_position = (x + 5, y)
    cv2.putText(image, text, text_position, FONT_FACE, FONT_SIZE, color, thickness, lineType=cv2.LINE_AA)
         
def drawHorizontalLineandValue(image, z1, z2, color, value, unit):
    thickness   = 1
    x1, y1 = z1
    x2, y2 = z2
    x = math.floor((x1 + x2) / 2)
    y = math.floor((y1 + y2) / 2)
    cv2.line(image, (x1, y), (x2, y), color, thickness)

    # Measurement value
    match unit:
        case Unit.PIXELS:
            units = ' pixels' 
        case Unit.MM:
            units = 'mm'
        case Unit.CM:
            units = 'cm'
        case _:
            units = 'units'
    text          = "{}".format(round(value, 1)) + units
    text_position = (x, y + 5)
    cv2.putText(image, text, text_position, FONT_FACE, FONT_SIZE, color, thickness, lineType=cv2.LINE_AA)
         