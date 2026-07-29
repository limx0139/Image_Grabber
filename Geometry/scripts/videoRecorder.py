import csv
from datetime import datetime
from pathlib import Path
import cv2
class recorder:
    
    def __init__(self):

        size = (640, 480)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        timestr = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        Path("logs/").mkdir(parents=True, exist_ok=True)
        Path("logs/video").mkdir(parents=True, exist_ok=True)
        self._out = cv2.VideoWriter(r'logs/videos/'+timestr+'.avi', fourcc, 20.0, size)


    def record(self, frame):
        self._out.write(frame)
    def stopRecord(self):
        self._out.release()

      
        
      
          
          
        
