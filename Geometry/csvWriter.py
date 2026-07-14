import csv

class csvWriter:
    
    def __init__(self, numVerticalROI, numHorizontalROI):
        self._file = None
        self._numVerticalROI = numVerticalROI
        self._numHorizontalROI = numHorizontalROI
    def writeHeaders():
      with open('names.csv', 'w', newline='') as csvfile:
      fieldnames = ['first_name', 'last_name']
    
    
with open("demofile.txt", "a") as f:
  f.write("Now the file has more content!")

#open and read the file after the appending:
with open("demofile.txt") as f:
  print(f.read())