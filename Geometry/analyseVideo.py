# Example Script to draw max and min temperature onto the image using opencv2

from asyncio import graph
import sys


import cv2
from matplotlib import pyplot as plt
import numpy as np
from draw import drawVerticalLineandValue, drawVerticalROI
from geometryMeasurement import measureVerticalGeometry
import ametekframegrabber as fg
from canny import auto_canny, removeReflection

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE  = (255, 0, 0)
FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX

Frame_WIDTH = 640
Frame_HEIGHT = 480

class MainThread:

    def __init__(self, ipAddress, numVerticalROIs, numHorizontalROIs, reflection_index=0.9):
        self._ipAddress = ipAddress
        self._numVerticalROIs = numVerticalROIs
        self._numHorizontalROIs = numHorizontalROIs
        self._reflection_index = reflection_index        
        if self._numVerticalROIs == 0 or self._numHorizontalROIs == 0:
            raise ValueError("Number of vertical and horizontal ROIs must be greater than zero.")
            
        self._verticalGeometry = self._numVerticalROIs * [0]  # Initialize the vertical geometry list with zeros
        self._horizontalGeometry = self._numHorizontalROIs * [0]  # Initialize the horizontal geometry list with zeros
        print("test")
        self._verticalGeometryHistory = np.empty((0, len(self._verticalGeometry)))  # Initialize an empty array to store vertical geometry measurements
        self._horizontalGeometryHistory = np.empty((0, len(self._horizontalGeometry)))  # Initialize an empty array to store horizontal geometry measurements
    def run(self, videoPath):
        """
        Main loop to process thermal frames and update the server.
        """
        """
        Loads the video file and processes each frame to detect and draw lines.
        """
        cap = cv2.VideoCapture(videoPath)

        # Check if the video opened correctly
        if not cap.isOpened():
            print("Error: Could not open video file.")
            exit()

        # Read and process video frames
        while True:
            noObject = False
            ret, image = cap.read()

            if not ret:
                break   # No more frames -> exit loop

            # Apply Canny edge detection to the thermal image
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            max_value = np.max(gray)
            min_value = np.min(gray)
            if max_value - min_value < 50:
                noObject = True
            if not noObject:
                removed_reflection = removeReflection(gray, self._reflection_index)
                cv2.imshow('Remove Reflections', removed_reflection)
                edged = auto_canny(removed_reflection, sigma = 0.1, blurIndex = 5)
                cv2.imshow('Canny Edges', edged)
            
                drawVerticalROI(image, WHITE, self._numVerticalROIs)
                print(f"Vertical Geometry: {self._verticalGeometry}")
                coords = measureVerticalGeometry(self._verticalGeometry, edged, self._numVerticalROIs)
                currentVerticalGeometry = self._verticalGeometry.copy()  # Make a copy of the current vertical geometry

                
                for x in range(len(coords)):
                    # Draw the vertical line and measurement on the image
                    y1 = coords[x][0]
                    y2 = coords[x][1]
                    x_pos = coords[x][2]
                    if y1 is not None and y2 is not None:  # Only draw if both y1 and y2 are valid
                        drawVerticalLineandValue(image, (x_pos, y1), (x_pos, y2), BLACK, currentVerticalGeometry[x])
                cv2.imshow('Frames', image)
            else:   
                drawVerticalROI(image, WHITE, self._numVerticalROIs)
                cv2.imshow('Frames', image)

            # Press Q to quit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
               break

def main():
    """
    Main entry point.
    """
    # Get the IP address from command line argument
    # With an IP address of 0 the first compatible camera will be chosen
    ipAddress = "10.1.10.102"
    if len(sys.argv) >= 2:
       ipAddress = int(sys.argv[1])
       return
       client = None
       
    try:
      client = MainThread(ipAddress, 20, 15)

    except Exception as ex:
        print(ex)
        return
    client.run("ForgingVideos/video2.mp4")


if __name__ == "__main__":
    main()