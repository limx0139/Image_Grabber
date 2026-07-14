
import math

import cv2
FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SIZE = 0.4

def drawVerticalROI(image, color, numVerticalROIs):

      thickness   = 1
      num_rows, num_cols = image.shape[:2]
      width = num_cols // numVerticalROIs
      for x in range(width, num_cols, width):
          cv2.line(image, (x, 0), (x, num_rows), color, thickness)

def drawVerticalLineandValue(image, z1, z2, color, value):
    thickness   = 1
    x1, y1 = z1
    x2, y2 = z2
    x = math.floor((x1 + x2) / 2)
    y = math.floor((y1 + y2) / 2)
    cv2.line(image, (x, y1), (x, y2), color, thickness)

    # Measurement value
    text          = "{}".format(round(value, 1))
    text_position = (x + 5, y)
    cv2.putText(image, text, text_position, FONT_FACE, FONT_SIZE, color, thickness, lineType=cv2.LINE_AA)
         