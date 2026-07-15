from enum import Enum

import cv2


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE  = (255, 0, 0)
FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX

Frame_WIDTH = 640
Frame_HEIGHT = 480

class Unit(Enum):
    PIXELS = 1
    MM = 2
    CM = 3
    UNITS = 4