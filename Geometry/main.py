# Example Script to draw max and min temperature onto the image using opencv2

from asyncio import graph
import asyncio
import logging
import sys
import threading
import time

import cv2
from matplotlib import pyplot as plt
import numpy as np
from csvDumper import csvWriter
from opcua_server import startServer
from draw import drawHorizontalLineandValue, drawHorizontalROI, drawVerticalLineandValue, drawVerticalROI
from geometryMeasurement import measureHorizontalGeometry, measureVerticalGeometry
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

    def __init__(self, ipAddress, serverEndpoint, numVerticalROIs, numHorizontalROIs, reflection_index=0.5):
        self._ipAddress = ipAddress
        self._numVerticalROIs = numVerticalROIs
        self._numHorizontalROIs = numHorizontalROIs
        self._reflection_index = reflection_index
        # Informs the server thread that a new frame is available to update.
        self._serverFrameAvailable = threading.Event()
        self._geometryLock = threading.Lock()
        # Connects to device with IPAddress 10.1.10.102
        self._connectedDevice = fg.connect(ipAddress)
        # Instantiates the Device API for that device
        self._Device = fg.Device(self._connectedDevice)
        # Starts a background thread streaming the camera
        self._Device.startStreaming()
        
        
        if self._numVerticalROIs == 0 or self._numHorizontalROIs == 0:
            raise ValueError("Number of vertical and horizontal ROIs must be greater than zero.")
            
        self._verticalGeometry = self._numVerticalROIs * [0]  # Initialize the vertical geometry list with zeros
        self._horizontalGeometry = self._numHorizontalROIs * [0]  # Initialize the horizontal geometry list with zeros
        print("test")
        self._verticalGeometryHistory = np.empty((0, len(self._verticalGeometry)))  # Initialize an empty array to store vertical geometry measurements
        self._horizontalGeometryHistory = np.empty((0, len(self._horizontalGeometry)))  # Initialize an empty array to store horizontal geometry measurements
        self._stopEvent = threading.Event()
        self._stopEvent.clear()  # Ensure the stop event is cleared at the start
        self._serverEndpoint = serverEndpoint
        self._serverThread = threading.Thread(target=asyncio.run, args=(startServer(self._serverEndpoint, numVerticalROIs, numHorizontalROIs, self._verticalGeometry, self._horizontalGeometry, self._serverFrameAvailable, self._geometryLock, self._stopEvent),))

        self._csvWriter = csvWriter(self._numVerticalROIs, self._numHorizontalROIs)
        self._csvWriter.writeHeaders()
        
    def run(self):
        """
        Main loop to process thermal frames and update the server.
        """
        _logger = logging.getLogger(__name__)
        _logger.info("Starting main loop!")
        plt.ion()
        self._serverThread.start()
        loops = 0
        startTime = time.time()
        while(True):
            # Get the latest thermal frame if there is one
            if loops % 1000 == 0:
                endTime = time.time()
                elapsedTime = endTime - startTime
                print(f"Camera processed 1000 frames in {elapsedTime:.2f} seconds. Average FPS: {1000 / elapsedTime:.2f}")
                startTime = time.time()
                
            try:
                # Wait for background thread to send a frame
                self._Device._frame_availale.wait()
                # Temparorily block background thread from overwriting the frame while we copy it for processing.
                with self._Device._frame_event_lock:
                    if self._Device._frame_event is None:
                        continue
                    frame = fg.ThermalFrame(self._Device._frame_event)
                    image = np.copy(frame._image)
                    
        # ------------------------------------------------------------------------------------------------------ 
                # Here is where you have access to the thermal frame!
        # ------------------------------------------------------------------------------------------------------    
                
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                max_value = np.max(gray)
                min_value = np.min(gray)

                image2 = image.copy()
                drawVerticalROI(image, WHITE, self._numVerticalROIs)
                drawHorizontalROI(image2, WHITE, self._numHorizontalROIs)
                
                if max_value - min_value < 100:
                    # self._verticalGeometryHistory = np.append(self._verticalGeometryHistory, [np.empty((0, len(self._verticalGeometry)))], axis=0)
                    cv2.imshow('Frames', image)
                    cv2.imshow('Frames2', image2)
                    coords1 = None
                    coords2 = None
                    currentVerticalGeometry = None
                    currentHorizontalGeometry = None
                    with self._geometryLock:
                        self._verticalGeometry = self._numVerticalROIs * [0] 
                        self._horizontalGeometry = self._numHorizontalROIs * [0]   
                    currentVerticalGeometry = None
                    currentHorizontalGeometry = None   
                    
                else:
                    removed_reflection = removeReflection(gray, self._reflection_index)
                    cv2.imshow('Remove Reflections', removed_reflection)
                    edged = auto_canny(removed_reflection)
                    cv2.imshow('Canny Edges', edged)
                    with self._geometryLock:
                        coords1 = measureVerticalGeometry(self._verticalGeometry, edged, self._numVerticalROIs)
                        coords2 = measureHorizontalGeometry(self._horizontalGeometry, edged, self._numHorizontalROIs)
                        currentVerticalGeometry = self._verticalGeometry.copy()  # Make a copy of the current vertical geometry
                        currentHorizontalGeometry = self._horizontalGeometry.copy()  # Make a copy of the current horizontal geometry
                    # self._verticalGeometryHistory = np.append(self._verticalGeometryHistory, [currentVerticalGeometry], axis=0)
                    # self._horizontalGeometryHistory = np.append(self._horizontalGeometryHistory, [currentHorizontalGeometry], axis=0)
                    # if len(self._verticalGeometryHistory) > 5000:
                    #     self._verticalGeometryHistory = self._verticalGeometryHistory[len(self._verticalGeometryHistory)-1000:len(self._verticalGeometryHistory)]
                    
                    
                    # Signal the server thread that a new frame is available
                self._serverFrameAvailable.set() 
                if coords1 is not None and coords2 is not None:
                    for x in range(len(coords1)):
                        # Draw the vertical line and measurement on the image
                        y1 = coords1[x][0]
                        y2 = coords1[x][1]
                        x_pos = coords1[x][2]
                        if y1 is not None and y2 is not None:  # Only draw if both y1 and y2 are valid
                            drawVerticalLineandValue(image, (x_pos, y1), (x_pos, y2), BLACK, currentVerticalGeometry[x])
                    for y in range(len(coords2)):
                        # Draw the horizontal line and measurement on the image
                        if coords2[y] is not None: 
                            drawHorizontalLineandValue(image2, coords2[y][0], coords2[y][1], BLACK, currentHorizontalGeometry[y])
                self._csvWriter.writeLine(currentVerticalGeometry + currentHorizontalGeometry)
                cv2.imshow('Frames', image)
                cv2.imshow('Frames2', image2)
                
                # if loops == 0:  # Initialize the plot on the first loop
                #     ax, lines = self.initPlot()
                    
                # if loops % 10 == 0:  # Update the plot every 10 loops
                #     self._updatePlot(ax, lines)

                    
                # Check for keyboard inputs indicating that the user wants to quit by pressing the q key
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    
                    self._stopEvent.set()  # Signal the server thread to stop
                    self._serverFrameAvailable.set()
                    self._serverThread.join()
                    break
                
        # ------------------------------------------------------------------------------------------------------ 
                # Here is where the thermal frame falls out of scope!
        # ------------------------------------------------------------------------------------------------------  
            
                # Clear the event flag to wait for the next time the flag is set
                self._Device._frame_availale.clear()
                loops += 1
            except KeyboardInterrupt:
                break
        # Clean up
        cv2.destroyAllWindows()
        self._Device.stopStreaming()
        self._Device.disconnect()
        
    def initPlot(self):
        """
        Initializes the plot for vertical geometry measurements.
        """
        plt.figure()
        plt.title('Vertical Geometry Measurements')
        plt.xlabel('Frame Number')
        plt.ylabel('Length (pixels)')
        ax = plt.gca()
        ax.set_ylim(0, 500)
        lines = []
        for i in range(self._numVerticalROIs):
            lines.append(plt.plot(range(len(self._verticalGeometryHistory)), self._verticalGeometryHistory[:,i], label=f'ROI {i+1}'))
        plt.legend()
        return ax, lines
    def _updatePlot(self, ax, lines):
        """
        Updates the plot with the latest vertical geometry measurements.
        """
        for i in range(len(lines)):
            lines[i][0].set_data(range(len(self._verticalGeometryHistory)), self._verticalGeometryHistory[:, i])
        ax.set_xlim(max(0, len(self._verticalGeometryHistory)-501), len(self._verticalGeometryHistory)-1)
        
        plt.draw()
        plt.pause(0.01)

def main():
    """
    Main entry point.
    """
    # Get the IP address from command line argument
    # With an IP address of 0 the first compatible camera will be chosen
    ipAddress = "10.1.10.102"
    serverEndpoint = "opc.tcp://0.0.0.0:4840/freeopcua/server/"
    if len(sys.argv) >= 2:
       ipAddress = int(sys.argv[1])
       return
       client = None
    
    try:
      client = MainThread(ipAddress,serverEndpoint, 10, 10)

    except Exception as ex:
        print(ex)
        return
    client.run()


if __name__ == "__main__":
    main()