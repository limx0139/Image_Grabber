# Example Script to draw max and min temperature onto the image using opencv2
#test
import cv2
import numpy as np
import ametekframegrabber as fg


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