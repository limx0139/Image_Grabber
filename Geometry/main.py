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
from scripts import videoRecorder
from scripts.csvDumper import csvWriter
from scripts.opcua_server import startServer
from scripts.draw import drawHorizontalLineandValue, drawHorizontalROI, drawOverlay, drawVerticalLineandValue, drawVerticalROI
from scripts.geometryMeasurement import convertUnits, measureHorizontalGeometry, measureVerticalGeometry
import scripts.ametekframegrabber as fg
from scripts.canny import auto_canny, removeReflection
import scripts.globalParameters as GLOBAL


    

class MainThread:

    def __init__(self, ipAddress = "10.1.10.102", serverEndpoint = "opc.tcp://0.0.0.0:4840/freeopcua/server/", numVerticalROIs = 10, numHorizontalROIs = 10, reflection_index=0.9, cannySigma = 0.33, blurIndex = 5, pixelConversionIndex = 1, unit = GLOBAL.Unit.PIXELS, csvDump = True, plotGraph = False, showImages = 2):
        # Initialises connection with camera
        try:
            
            self._ipAddress = ipAddress
            self._connectedDevice = fg.connect(ipAddress)
            self._Device = fg.Device(self._connectedDevice)
            # Starts a background thread streaming the camera
            print("------------Current Settings------------")
            print("Temperature Range: "+ str(self._Device.getTemperatureRange()))
            print("----------------------------------------")
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
        self._serverThread = threading.Thread(target=asyncio.run, args=(startServer(self._serverEndpoint, numVerticalROIs, numHorizontalROIs, self._verticalGeometry, self._horizontalGeometry, self._serverFrameAvailable, self._geometryLock, self._stopEvent, units = unit),))
        
        # Initialise csvLogger
        self._csvDump = csvDump
        try:
            self._csvWriter = csvWriter(self._numVerticalROIs, self._numHorizontalROIs)
            if self._csvDump:
                self._csvWriter.writeHeaders()
        except Exception as ex:
            print(ex + ", CSV logger failed to initialise.")
            raise ex
        
        # Flag to control whether graphs are plotted
        self._plotGraph = plotGraph
        
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
        recording = False
        recorder = None
        framerate = 47
        while(True):
            # Get the latest thermal frame if there is one
            if loops != 0 and loops % 1000 == 0:
                endTime = time.time()
                elapsedTime = endTime - startTime
                framerate = 1000 / elapsedTime+0.00001
                print(f"Camera processed 1000 frames in {elapsedTime:.2f} seconds. Average FPS: {framerate:.2f}")
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
                    temperatureMap = np.copy(frame._tempData)
                    
        # ------------------------------------------------------------------------------------------------------ 
                # Here is where you have access to the thermal frame!
        # ------------------------------------------------------------------------------------------------------    
                
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                image2 = image.copy()

                # Skip processing if no object is found, ie. difference between min and max value is small
                max_value = np.max(temperatureMap)
                min_value = np.min(temperatureMap)
                if max_value - min_value < GLOBAL.SENSITIVITY:
                    # No object found
                    coords1 = None
                    coords2 = None
                    currentVerticalGeometry = None
                    currentHorizontalGeometry = None
                    with self._geometryLock:
                        self._verticalGeometry = self._numVerticalROIs * [0] 
                        self._horizontalGeometry = self._numHorizontalROIs * [0]   
                    currentVerticalGeometry = self._numVerticalROIs * [0] 
                    currentHorizontalGeometry = self._numHorizontalROIs * [0]    
                
                  
                else:
                    # Process the image 
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
                    drawVerticalROI(image, self._numVerticalROIs)
                    drawHorizontalROI(image2, self._numHorizontalROIs)
                    # drawOverlay(image, recording)
                    #Draw lengths on the images
                    if coords1 is not None and coords2 is not None:
                        for x in range(len(coords1)):
                            # Draw the vertical line and measurement on the image
                            if coords1[x] is not None:  # Only draw if both y1 and y2 are valid
                                drawVerticalLineandValue(image, coords1[x][0], coords1[x][1], GLOBAL.BLACK, currentVerticalGeometry[x], unit = self._unit)
                        for y in range(len(coords2)):
                            # Draw the horizontal line and measurement on the image
                            if coords2[y] is not None: 
                                drawHorizontalLineandValue(image2, coords2[y][0], coords2[y][1], GLOBAL.BLACK, currentHorizontalGeometry[y], unit = self._unit)
                    cv2.imshow('Vertical ROIs', image)
                    cv2.imshow('Horizontal ROIs', image2)
                 
                # If setting to create csv log file is on, write the new line onto the csv file
                # It may be better to create a buffered system to update the csv file every couple of loops, but this likely introduces unnecessary complexity at this stage; read/write operations are not the bottleneck, the opcua server is.   
                # Might change it to log every second with the image for a middleground
                if self._csvDump:
                    self._csvWriter.writeLine(currentVerticalGeometry + currentHorizontalGeometry)
                    # Save an image 30 frames, approx every second
                    if loops % 60 == 0:
                        self._csvWriter.writeImageV(image)
                        self._csvWriter.writeImageH(image2)
                

                


                    
                # Check for keyboard inputs indicating that the user wants to quit by pressing the q key
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    if recording:
                        recorder.stopRecord()
                        recorder = None
                    self._stopEvent.set()  # Signal the server thread to stop
                    self._serverFrameAvailable.set()
                    self._serverThread.join()
                    break
                elif key == ord('t'):
                    if not recording:
                        recording = True
                        recorder = videoRecorder.recorder(framerate, False)
                elif key == ord('r'):
                    if not recording:
                        recording = True
                        recorder = videoRecorder.recorder(framerate, True)
                elif key == ord('y'):
                    if recorder is not None:
                        recording = False
                        recorder.stopRecord()
                        recorder = None
                elif key == ord('s'):
                    self._csvWriter.writeImageManualH(image2)
                    self._csvWriter.writeImageManualV(image)
                if recording:
                    if recorder._colour:
                        recorder.record(image)
                    else:
                        recorder.record(temperatureMap)
                
        # ------------------------------------------------------------------------------------------------------ 
                # Here is where the thermal frame falls out of scope!
        # ------------------------------------------------------------------------------------------------------  
            
                # Clear the event flag to wait for the next time the flag is set
                self._Device._frame_availale.clear()
                loops += 1
            except Exception as ex:
                # Kill all child threads to close gracefully on keyboard interrrupt
                print(ex)
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
    ip = GLOBAL.IP_ADDRESS
    endpoint = GLOBAL.SERVER_ENDPOINT
    pixelConversion = GLOBAL.PIXEL_CONVERSION_RATE
    unitEnum = GLOBAL.Unit.PIXELS
    inputVerticalROI = GLOBAL.NUM_VERTICAL_ROIS
    inputHorizontalROI = GLOBAL.NUM_HORIZONTAL_ROIS
    makeLogs = GLOBAL.MAKE_LOGS

    if len(sys.argv) == 7:
        ip = sys.argv[1]
        endpoint = sys.argv[2]
        inputVerticalROI = int(sys.argv[3])
        inputHorizontalROI = int(sys.argv[4])
        pixelConversion = int(sys.argv[5])
        units = str(sys.argv[6])
        match units:
            case 'pixels':
                unitEnum = GLOBAL.Unit.PIXELS
            case 'mm':
                unitEnum = GLOBAL.Unit.MM
            case 'cm':
                unitEnum = GLOBAL.Unit.CM
            case '_':
                raise Exception('InputError: Invalid unit input')
    elif len(sys.argv) != 1:
        raise Exception('InputError: Expected 1 or 7 arguments.')


    client = None
    
    try:
      client = MainThread(ipAddress = ip ,serverEndpoint = endpoint, numVerticalROIs = inputVerticalROI, numHorizontalROIs = inputHorizontalROI, csvDump=makeLogs, unit = unitEnum, pixelConversionIndex= pixelConversion)

    except Exception as ex:
        raise ex
    client.run()



if __name__ == "__main__":
    main()