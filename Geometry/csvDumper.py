import csv
from datetime import datetime
datetime.now().strftime("%H:%M:%S.%f")
from pathlib import Path
class csvWriter:
    
    def __init__(self, numVerticalROI, numHorizontalROI):
        self._file = None
        self._numVerticalROI = numVerticalROI
        self._numHorizontalROI = numHorizontalROI
        timestr = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self._fileName = r'logs/'+ 'geometryLogs_' + timestr + '.csv' 
        Path("logs/").mkdir(parents=True, exist_ok=True)
    def writeHeaders(self):
      with open(self._fileName, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header = []
        header.append('Time')
        for i in range(self._numVerticalROI):
          header.append('verticalROI'+str(i+1))
        for i in range(self._numHorizontalROI):
          header.append('horizontalROI'+str(i+1))
        writer.writerow(header)
    def writeLine(self, line):
      if len(line) != self._numHorizontalROI + self._numVerticalROI:
        # Should throw exception, incorrect line data
        return
      with open(self._fileName, 'a', newline='') as csvfile:
        line.insert(0,datetime.now().strftime("%H:%M:%S.%f"))
        writer = csv.writer(csvfile)
        writer.writerow(line)
    def writeBufferedLine(self, bufferedLine):
      #TODO
      return
        
      
          
          
        
    
    
# with open("demofile.txt", "a") as f:
#   f.write("Now the file has more content!")

# #open and read the file after the appending:
# with open("demofile.txt") as f:
#   print(f.read())
timestr = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
print('geometryLogs_' + timestr + '.csv')
print(timestr)
fun = csvWriter(5, 5)
fun.writeHeaders()
fun.writeLine([1,2,3,4,5,6,7,8,9,10])