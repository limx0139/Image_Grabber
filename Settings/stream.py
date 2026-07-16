# Example Script to draw max and min temperature onto the image using opencv2
#test
import cv2
import numpy as np
import ametekframegrabber as fg
# Settings for the displayed fonts
FONT_FACE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SIZE = 0.4

# OpenCV colors (BGR)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE  = (255, 0, 0)

def drawOverlay(image):
    """
    Superimposes an overlay over the false color image.
    """

    if len(opticsText) != 0:
        opticsText = ' {}'.format(opticsText)

    # Overlay text
    text = [
            'i: MoveIn', 
            'o: MoveOut',
            'q: Quit']

    # Text font face
    thickness = 1
    line_margin = 10

    # Overlay position
    x = image.shape[1] - 275
    y = 25

    # Draw overlay
    for i, line in enumerate(text):
        line_height = cv2.getTextSize(line, FONT_FACE, FONT_SIZE, thickness)[0][1]
        position    = (x, y + i * (line_height + line_margin))

        cv2.putText(image, line, position, FONT_FACE, FONT_SIZE, BLACK, thickness+1, lineType = cv2.LINE_AA)
        cv2.putText(image, line, position, FONT_FACE, FONT_SIZE, GREEN, thickness, lineType = cv2.LINE_AA)
    
def streamWithFocusAdjust(Device):

    """
    Streams video with option to adjust focus
    """
    # Starts a background thread streaming the camera
    Device.startStreaming()

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
            drawOverlay(image)
            cv2.imshow('Frames', image)
            # Check for keyboard inputs indicating that the user wants to quit by pressing the q key
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('i'):
                Device.adjustFocus(fg.FocusAdjustment.MoveIn, 1)
            elif key == ord('o'):
                Device.adjustFocus(fg.FocusAdjustment.MoveOut, 1)
            
    # ------------------------------------------------------------------------------------------------------ 
            # Here is where the thermal frame falls out of scope!
    # ------------------------------------------------------------------------------------------------------  
        
            # Clear the event flag to wait for the next time the flag is set
            Device._frame_availale.clear()
        except KeyboardInterrupt:
            break
    # Clean up
    cv2.destroyAllWindows()
    Device.stopStreaming()
    Device.disconnect()
    
    
def stream(Device):

    """
    Streams video
    """
    # Starts a background thread streaming the camera
    Device.startStreaming()

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
            cv2.imshow('Frames', image)
            # Check for keyboard inputs indicating that the user wants to quit by pressing the q key
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            
    # ------------------------------------------------------------------------------------------------------ 
            # Here is where the thermal frame falls out of scope!
    # ------------------------------------------------------------------------------------------------------  
        
            # Clear the event flag to wait for the next time the flag is set
            Device._frame_availale.clear()
        except KeyboardInterrupt:
            break
    # Clean up
    cv2.destroyAllWindows()
    Device.stopStreaming()
    Device.disconnect()