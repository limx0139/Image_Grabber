# Example Script to draw max and min temperature onto the image using opencv2

from asyncio import graph

import cv2
from matplotlib import pyplot as plt
import numpy as np
from geometryMeasurement import measureVerticalGeometry
import ametekframegrabber as fg
from canny import auto_canny, removeReflection

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE  = (255, 0, 0)
FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SIZE = 0.4
ROI_WIDTH = 100
ROI_HEIGHT = 100





def drawVerticalROI(image, color, ROI_WIDTH):
      """
      Draws a marker at the position of a temperature measurement and its value next to it.
      """

      thickness   = 1
      num_rows, num_cols = image.shape[:2]
      for x in range(ROI_WIDTH, num_cols, ROI_WIDTH):
          cv2.line(image, (x, 0), (x, num_rows), color, thickness)
      
      

# Connects to device with IPAddress 10.1.10.102
connectedDevice = fg.connect("10.1.10.102")
# Instantiates the Device API for that device
Device = fg.Device(connectedDevice)
# Starts a background thread streaming the camera
Device.startStreaming()
plt.ion()
verticalGeometry = np.empty((0, 7))  # Initialize an empty array to store vertical geometry measurements
loops = 0
while(True):
    # Get the latest thermal frame if there is one
    try:
        # Wait for background thread to send a frame
        Device._frame_availale.wait()
        # Temparorily block background thread from overwriting the frame while we copy it for processing.
        with Device._frame_event_lock:
            if Device._frame_event is None:
                continue
            frame = fg.ThermalFrame(Device._frame_event)
            image = np.copy(frame._image)
            
# ------------------------------------------------------------------------------------------------------ 
        # Here is where you have access to the thermal frame!
# ------------------------------------------------------------------------------------------------------    
        num_rows, num_cols = image.shape[:2]
        # Apply Canny edge detection to the thermal image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        removed_reflection = removeReflection(gray, reflection_index=0.5)
        edged = auto_canny(removed_reflection)
        cv2.imshow('Canny Edges', edged)
        
        drawVerticalROI(image, WHITE, ROI_WIDTH)
        verticalGeometry = np.append(verticalGeometry, [measureVerticalGeometry(edged, ROI_WIDTH)], axis=0)
        cv2.imshow('Frames', image)
        
        if loops == 0:  # Initialize the plot on the first loop
            plt.figure()
            plt.title('Vertical Geometry Measurements')
            plt.xlabel('Frame Number')
            plt.ylabel('Length (pixels)')
            ax = plt.gca()
            ax.set_ylim(0, 500)
            lines = []
            for i in range(num_cols // ROI_WIDTH):
                lines.append(plt.plot(range(len(verticalGeometry)), verticalGeometry[:,i], label=f'ROI {i+1}'))
            plt.legend()
            
        if loops % 10 == 0:  # Update the plot every 10 loops
            for i in range(len(lines)):
                lines[i][0].set_data(range(len(verticalGeometry)), verticalGeometry[:, i])
            ax.set_xlim(max(0, len(verticalGeometry)-501), len(verticalGeometry)-1)
            
            plt.draw()
            plt.pause(0.01)
            
        # Check for keyboard inputs indicating that the user wants to quit by pressing the q key
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        
# ------------------------------------------------------------------------------------------------------ 
        # Here is where the thermal frame falls out of scope!
# ------------------------------------------------------------------------------------------------------  
     
        # Clear the event flag to wait for the next time the flag is set
        Device._frame_availale.clear()
        loops += 1
    except KeyboardInterrupt:
        break
# Clean up
cv2.destroyAllWindows()
Device.stopStreaming()
Device.disconnect()