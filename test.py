import clr
import os
import sys
import threading
import cv2
import numpy as np
import os
# Finds the directory of the LandImagerSDK.dll, which should be in the same directory as the script
cwd = os.getcwd()
assemblyLocation = cwd+"\\LandImagerSDK.dll"
print(assemblyLocation)
clr.AddReference(assemblyLocation)
clr.AddReference("System")

import LandImagerSDK as li
import System.Net.IPAddress as IPAddress

class ConnectLANDDialogue:
     
    def __init__(self):
        # Stores the ConnectionInfo of the connected device
        self._connectDevice = li.Model.ConnectionInfo(IPAddress.Parse("127.0.0.1"), IPAddress.Parse("255.255.0.0"), 1040, li.Enums.IPMode.Static, "12345", li.Enums.ImagerModel.ARC)
        # List of Devices found
        self._discoveredDevices = []
        # DeviceAPI for selected device
        self._connectedDevice = None

    
    def discoverDevices(self):
        devices = li.Discovery.DiscoverDevices()

        self._discoveredDevices.clear()
        for device in devices:
            self._discoveredDevices.append(self.ConnectionItem(device.ConnectionInfo))
    
    def connectDevice(self):
        choice = 0
        
        if len(sys.argv) == 1:
            choice = 0
        elif isinstance(sys.argv[1], int) and self._discoveredDevices.count >= sys.argv[1]:
            choice = sys.argv[1]-1
        else:
            print("Error: Invalid argument")
        
        connectDevice = self._discoveredDevices[choice].getConnectionInfo()
        # There is an additional check in the example code that the ip addresses are valid. This is skipped here as the ip address is not user input.
        if connectDevice is not None:
            self._connectedDevice = li.Discovery.DirectConnect(connectDevice)
                
    class ConnectionItem:
        def __init__(self, connectionInfo):
            self._connectionInfo = connectionInfo
    

        def getConnectionInfo(self):
            return self._connectionInfo

        def toString(self):
            self._connectionInfo.IPAddress.ToString()
 
class FrameGrabber:
    def __init__(self, DeviceAPI):
        # DeviceAPI for selected device
        self._connectedDevice = DeviceAPI
        self._currentFrame = None
        # Threading lock to sync the frame grabbing and image processing threads
        self._frame_event_lock    = threading.Lock()
        self._frame_event         = None
        self._frame_event_updated = False
        # Writable Bitmap format the original uses
        self._bmp = None
        
    def connect(self):
        if self._connectedDevice is not None:
            self._connectedDevice.ThermalFrameAvailable += self.onFrame
    def startStreaming(self):
        if self._connectedDevice is not None:
            print("Start Streaming")
            self._connectedDevice.StartStreaming()
    def stopStreaming(self):
        if self._connectedDevice is not None:
            self._connectedDevice.StopStreaming()
    def disconnect(self):
        if self._connectedDevice is not None:
            self._connectedDevice.ThermalFrameAvailable -= self.onFrame
            self._connectedDevice.Disconnect()
    def onFrame(self, source, args):
        
        with self._frame_event_lock:
            # Store a copy of the event to be processed in the main thread. The provided event object is reused
            # by the SDK once the callback returns.
            print("onFrame using lock!")
            self._frame_event         = args.ThermalFrame.Clone()
            self._frame_event_updated = True
    
    # Main Thread set up to receive frames
    def runMain(self):
        self.connect()
        self.startStreaming()
        # # Create and start the image grabbing/processing thread
        # self._thread = threading.Thread(target=self.runListener)
        # self._thread.start()
        
        frame_event = None
        
        while(True):
            # Get the latest thermal frame if there is one
            try:
                with self._frame_event_lock:
                    if not self._frame_event_updated or self._frame_event is None:
                        continue

                    frame_event = self._frame_event
                    self._frame_event_updated = False
                    print("Frame received on Main")
                #B8G8R8A8
                currentFrame = self._frame_event.GetTemperatureBitmap()
                python_bytes = bytes(currentFrame.PixelData)
                numpy_bytes = np.frombuffer(python_bytes, dtype=np.uint8)
                newarr = numpy_bytes.reshape(frame_event.FrameHeight, frame_event.FrameWidth, 4)
                cv2.imshow('Grabbed', newarr)
        
                # Check for keyboard inputs indicating that the user wants to quit by pressing the q key
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break

        
        
            except KeyboardInterrupt:
                break
        # Clean up
        cv2.destroyAllWindows()
        self.stopStreaming()
        self.disconnect()

def main():
    """
    Main entry point.
    """
    # Connect to device
    connection = ConnectLANDDialogue()
    print(connection._discoveredDevices)
    connection.discoverDevices()
    print(connection._discoveredDevices)
    if len(connection._discoveredDevices) == 0:
        print("No devices found")
        return
    connection.connectDevice()
    if connection._connectedDevice is not None:
        print("Connection Success")
        
    # Grab Frames
    frameGrabber = FrameGrabber(connection._connectedDevice)
    frameGrabber.runMain()
    return
    
    

if __name__ == "__main__":
    main()
