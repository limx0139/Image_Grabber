import csv
from datetime import datetime
import pathlib
import cv2
class recorder:
    
    def __init__(self, framerate, colour):

        size = (640, 480)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        timestr = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        pathlib.Path("logs/").mkdir(parents=True, exist_ok=True)
        pathlib.Path("logs/video").mkdir(parents=True, exist_ok=True)
        path = str(pathlib.Path().resolve())
        self._colour = colour
        self._out = cv2.VideoWriter(path + '/logs/video/'+ timestr+ '.avi', fourcc, framerate, size, colour)


    def record(self, frame):
        if self._colour:
            self._out.write(frame[:,:,0:3])
        else:
            self._out.write(frame)
    def stopRecord(self):
        self._out.release()

      
        
      
          
          
        
