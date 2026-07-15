# Example Script to draw max and min temperature onto the image using opencv2

import asyncio
from enum import Enum
import logging
import sys
import threading
import time

import cv2
from matplotlib import pyplot as plt
import numpy as np
from plotFuncs import initPlot, updatePlot
from csvDumper import csvWriter
from opcua_server import startServer
from draw import drawHorizontalLineandValue, drawHorizontalROI, drawVerticalLineandValue, drawVerticalROI
from geometryMeasurement import convertUnits, measureHorizontalGeometry, measureVerticalGeometry
import ametekframegrabber as fg
from canny import auto_canny, removeReflection
import enums


    

class MainThread:

    def __init__(self, ipAddress, serverEndpoint, numVerticalROIs = 10, numHorizontalROIs = 10, reflection_index=0.9, cannySigma = 0.33, blurIndex = 5, pixelConversionIndex = 1, unit = enums.Unit.PIXELS, csvDump = True, plotGraph = False, showImages = 2):
        # Initialises connection with camera
        try:
            self._ipAddress = ipAddress
            self._connectedDevice = fg.connect(ipAddress)
            self._Device = fg.Device(self._connectedDevice)
            # Starts a background thread streaming the camera
            self._Device.startStreaming()
        except Exception as ex:
            raise ex
        
        # Initialise local parameters for image processing
        self._reflection_index = reflection_index
        self._cannySigma = cannySigma
        self._blurIndex = blurIndex
        self._pixelConversionIndex = pixelConversionIndex
        self._unit = unit

        # Initialise local parameters for storing ROI data
        self._numVerticalROIs = numVerticalROIs
        self._numHorizontalROIs = numHorizontalROIs
        if self._numVerticalROIs == 0 or self._numHorizontalROIs == 0:
            raise ValueError("Number of vertical and horizontal ROIs must be greater than zero.")
        self._verticalGeometry = self._numVerticalROIs * [0]  
        self._horizontalGeometry = self._numHorizontalROIs * [0]  
        self._verticalGeometryHistory = np.empty((0, len(self._verticalGeometry)))  
        self._horizontalGeometryHistory = np.empty((0, len(self._horizontalGeometry)))  
        
        # Initialise threading parameters for server thread
        self._serverFrameAvailable = threading.Event() # Informs server when frame is available
        self._stopEvent = threading.Event() # Informs server to shut down
        self._stopEvent.clear()  # Ensure the stop event is cleared at the start
        self._geometryLock = threading.Lock() # Mutex to prevent both threads accessing (self._verticalGeometry and self._horizontalGeometry) at the same time
        self._serverEndpoint = serverEndpoint # OPCUA server endpoint
        self._serverThread = threading.Thread(target=asyncio.run, args=(startServer(self._serverEndpoint, numVerticalROIs, numHorizontalROIs, self._verticalGeometry, self._horizontalGeometry, self._serverFrameAvailable, self._geometryLock, self._stopEvent, unit = unit),))
        
        # Initialise csvLogger
        self._csvDump = csvDump
        try:
            if self._csvDump:
                self._csvWriter = csvWriter(self._numVerticalROIs, self._numHorizontalROIs)
                self._csvWriter.writeHeaders()
        except Exception as ex:
            print(ex + ", CSV logger failed to initialise.")
            raise ex
        
        # Flag to control whether graphs are plotted
        self._plotGraph = plotGraph
        
        # Enum to control what sort of images to show
        # 0: no images
        # 1: images
        # 2: images with ROI demarcated and lengths
        # 3: images with length
        self._showImages = showImages

            
        
    def run(self):
        """
        Main loop to process thermal frames and update the server.
        """
        _logger = logging.getLogger(__name__)
        _logger.info("Starting main loop!")
        if self._plotGraph:
            plt.ion()
            
        try:
            self._serverThread.start()
        except Exception as ex:
            print(ex + ", OPCUA Server Thread failed to run.")
            raise ex
        
        loops = 0
        startTime = time.time()
        while(True):
            # Get the latest thermal frame if there is one
            if loops != 0 and loops % 1000 == 0:
                endTime = time.time()
                elapsedTime = endTime - startTime
                print(f"Camera processed 1000 frames in {elapsedTime:.2f} seconds. Average FPS: {1000 / elapsedTime+0.0001:.2f}")
                startTime = time.time()
                
            try:
                # Wait for background thread to send a frame
                self._Device._frame_availale.wait()
                # Temparorily block background thread from overwriting the frame while we copy it for processing.
                with self._Device._frame_event_lock:
                    if self._Device._frame_event is None:
                        continue
                    frame = fg.ThermalFrame(self._Device._frame_event)
                    # Save a copy for the ThermalFrame
                    image = np.copy(frame._image)
                    
        # ------------------------------------------------------------------------------------------------------ 
                # Here is where you have access to the thermal frame!
        # ------------------------------------------------------------------------------------------------------    
                
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                
                if self._showImages:
                    image2 = image.copy()
                    drawVerticalROI(image, enums.WHITE, self._numVerticalROIs)
                    drawHorizontalROI(image2, enums.WHITE, self._numHorizontalROIs)
                
                # Skip processing if no object is found
                max_value = np.max(gray)
                min_value = np.min(gray)
                if max_value - min_value < 100:
                    # self._verticalGeometryHistory = np.append(self._verticalGeometryHistory, [np.empty((0, len(self._verticalGeometry)))], axis=0)
                    if self._showImages:
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
                
                # Process the image    
                else:
                    removed_reflection = removeReflection(gray, self._reflection_index)
                    edged = auto_canny(removed_reflection, sigma = self._cannySigma, blurIndex = self._blurIndex)
                    with self._geometryLock:
                        coords1 = measureVerticalGeometry(self._verticalGeometry, edged, self._numVerticalROIs)
                        coords2 = measureHorizontalGeometry(self._horizontalGeometry, edged, self._numHorizontalROIs)
                        convertUnits(self._verticalGeometry, self._pixelConversionIndex)
                        convertUnits(self._horizontalGeometry, self._pixelConversionIndex)
                        currentVerticalGeometry = self._verticalGeometry.copy()  # Make a copy of the current vertical geometry
                        currentHorizontalGeometry = self._horizontalGeometry.copy()  # Make a copy of the current horizontal geometry
                        
                    
                # Signal the server thread that a new frame is available
                self._serverFrameAvailable.set() 
                
                if self._showImages:
                    #Draw lengths on the images
                    if coords1 is not None and coords2 is not None:
                        for x in range(len(coords1)):
                            # Draw the vertical line and measurement on the image
                            y1 = coords1[x][0]
                            y2 = coords1[x][1]
                            x_pos = coords1[x][2]
                            if y1 is not None and y2 is not None:  # Only draw if both y1 and y2 are valid
                                drawVerticalLineandValue(image, (x_pos, y1), (x_pos, y2), enums.BLACK, currentVerticalGeometry[x])
                        for y in range(len(coords2)):
                            # Draw the horizontal line and measurement on the image
                            if coords2[y] is not None: 
                                drawHorizontalLineandValue(image2, coords2[y][0], coords2[y][1], enums.BLACK, currentHorizontalGeometry[y])
                    cv2.imshow('Frames', image)
                    cv2.imshow('Frames2', image2)
                    
                if self._csvDump:
                    self._csvWriter.writeLine(currentVerticalGeometry + currentHorizontalGeometry)

                
                
                # if loops == 0:  # Initialize the plot on the first loop
                #     ax, lines = initPlot()
                    
                # if loops % 10 == 0:  # Update the plot every 10 loops
                #     updatePlot(ax, lines)

                    
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
                # Kill all child threads to close gracefully on keyboard interrrupt
                self._stopEvent.set()  # Signal the server thread to stop
                self._serverFrameAvailable.set()
                self._serverThread.join()
                break
        # Clean up
        cv2.destroyAllWindows()
        self._Device.stopStreaming()
        self._Device.disconnect()
        

def main():
    """
    Main entry point.
    """
    # Get the IP address from command line argument
    # With an IP address of 0 the first compatible camera will be chosen
    ipAddress = "10.1.10.102"
    serverEndpoint = "opc.tcp://0.0.0.0:4840/freeopcua/server/"
    pixelConversion = 1
    if len(sys.argv) >= 3:
       #ipAddress = int(sys.argv[1])
       pixelConversion = int(sys.argv[2])
    
   
    client = None
    
    try:
      client = MainThread(ipAddress,serverEndpoint, numVerticalROIs = 10, numHorizontalROIs = 10, unit = enums.Unit.MM, pixelConversionIndex= pixelConversion)

    except Exception as ex:
        print(ex)
        return
    client.run()



if __name__ == "__main__":
    main()