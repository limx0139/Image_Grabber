# Example Script to draw max and min temperature onto the image using opencv2

import cv2
import numpy as np
import Landframegrabber as lfg

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE  = (255, 0, 0)
FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SIZE = 0.4

def drawMeasurement(image, position, value, color, bg_color):
      """
      Draws a marker at the position of a temperature measurement and its value next to it.
      """
      marker_type = cv2.MARKER_CROSS
      marker_size = 20
      thickness   = 1
      
      # Measurement position
      cv2.drawMarker(image, position, bg_color, markerType=marker_type, markerSize=marker_size+1, thickness=thickness+1, line_type=cv2.LINE_AA)
      #cv2.drawMarker(image, position, color, markerType=marker_size, markerSize=marker_size, thickness=thickness, line_type=cv2.LINE_AA)

      # Measurement value
      text          = "{}".format(round(value, 1))
      text_position = (position[0] + int(marker_size / 3), position[1] - int(marker_size / 3))
      cv2.putText(image, text, text_position, FONT_FACE, FONT_SIZE, bg_color, thickness+1, lineType=cv2.LINE_AA)
      cv2.putText(image, text, text_position, FONT_FACE, FONT_SIZE, color, thickness, lineType=cv2.LINE_AA)

# Connects to device with IPAddress 10.1.10.102
connection = lfg.connect("10.1.10.102")
# Instantiates the Device API for that device
Device = lfg.Device(connection._connectedDevice)
# Starts a background thread streaming the camera
Device.startStreaming()

while(True):
    # Get the latest thermal frame if there is one
    try:
        # Wait for background thread to send a frame
        Device._frame_availale.wait()
        # Temparorily block background thread from overwriting the frame while we process it.
        with Device._frame_event_lock:
            if Device._frame_event is None:
                continue
            frame = lfg.ThermalFrame(Device._frame_event)
        image = np.copy(frame._image)
        
        # Here is where you have access to the thermal frame!
        
        # Draw markers for maximum and minimum temperature
        drawMeasurement(image, frame._maxIndex, frame._maxTemp, RED, WHITE)
        drawMeasurement(image, frame._minIndex, frame._minTemp, BLUE, WHITE)
        cv2.imshow('Frames', image)
        # Check for keyboard inputs indicating that the user wants to quit by pressing the q key
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        
        # Here is where the thermal frame falls out of scope!
        Device._frame_availale.clear()
    except KeyboardInterrupt:
        break
# Clean up
cv2.destroyAllWindows()
Device.stopStreaming()
Device.disconnect()