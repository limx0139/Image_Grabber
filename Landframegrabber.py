import clr
import os
import threading
import cv2
import numpy as np
import os
from enum import Enum
# Finds the directory of the LandImagerSDK.dll, which should be in the same directory as the script
cwd = os.getcwd()
assemblyLocation = cwd+"\\LandImagerSDK.dll"
print(assemblyLocation)
clr.AddReference(assemblyLocation)
clr.AddReference("System")

# python.net Imports from clr
# Python.net is a dependency!
import LandImagerSDK as li
import System


#ENUMS
class Palette(Enum):
    Palette1 = 1
    Palette2 = 2
    Palette3 = 3
    Palette4 = 4
    Palette5 = 5
    
class Process(Enum):
    Show = 1
    GetData = 2

    
# Class that handles connection to the Ametek Camera
class ConnectLANDDialogue:
     
    def __init__(self):
        # List of Devices found
        self._discoveredDevices = []
        # DeviceAPI for selected device to be returned upon successful connection
        self._connectedDevice = None

    # Finds connectable devices and appends them to self._discoveredDevices
    def discoverDevices(self):
        devices = li.Discovery.DiscoverDevices()
        self._discoveredDevices.clear()
        for device in devices:
            self._discoveredDevices.append(self.ConnectionItem(device.ConnectionInfo))
    
    # Connects to a device of choice parsed in as input integer arg, choosing the arg-th device in self._discoveredDevices, counting from 0
    # TODO: Implement an Exception on invalid arg
    def connectDevice(self, arg):
        if not isinstance(arg, str):
            print("Error: Invalid argument")
        
        # search for device with matching IPAddress
        # Assume no two devices have the same IPAddress
        connection = None
        
        for device in self._discoveredDevices:
            print(device.toString())
            if device.toString() == arg:
                connection = device.getConnectionInfo()
        if connection is not None:
            self._connectedDevice = li.Discovery.DirectConnect(connection)
        else:
            print("No device with IP: "+ arg +" found.")
                
    class ConnectionItem:
        def __init__(self, connectionInfo):
            self._connectionInfo = connectionInfo
    

        def getConnectionInfo(self):
            return self._connectionInfo

        def toString(self):
            return self._connectionInfo.IPAddress.ToString()
 
class FrameGrabber:
    def __init__(self, DeviceAPI):
        # DeviceAPI for selected device
        self._connectedDevice = DeviceAPI
        self._currentFrame = None
        # Threading lock to sync the frame grabbing and image processing threads
        self._frame_event_lock    = threading.Lock()
        # Variable to store the ThermalFrame for processings
        self._frame_event         = None
        self._frame_event_updated = False
        
    def setColorPalette(self, choice):
        temp = None
        match choice:
            case Palette.Palette1:
                temp = li.Enums.Palette.Palette1
            case Palette.Palette2:
                temp = li.Enums.Palette.Palette2
            case Palette.Palette3:
                temp = li.Enums.Palette.Palette3
            case Palette.Palette4:
                temp = li.Enums.Palette.Palette4
            case Palette.Palette5:
                temp = li.Enums.Palette.Palette5
            case _:
                # Invalid Palette
                return
        self._connectedDevice.ColorPalette.SelectedPalette = temp
        # return self._connectedDevice.ColorPalette.Palette

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
            self._frame_event         = args.ThermalFrame.Clone()
            self._frame_event_updated = True
    
    # Main Thread set up to receive frames, arg process takes in an integer to choose how frame is processed
    def processFrame(self, process):
        self.connect()
        # This starts a background thread to send the ThermalFrames from the camera
        self.startStreaming()
        frame_event = None
        
        while(True):
            # Get the latest thermal frame if there is one
            try:
                with self._frame_event_lock:
                    if not self._frame_event_updated or self._frame_event is None:
                        continue

                    frame_event = self._frame_event
                    self._frame_event_updated = False
                match process:
                    case Process.Show:
                        # B8G8R8A8 Format
                        # Converts the C# bytes to a numpy array
                        currentFrame = self._frame_event.GetTemperatureBitmap()
                        python_bytes = bytes(currentFrame.PixelData)
                        numpy_bytes = np.frombuffer(python_bytes, dtype=np.uint8)
                        newarr = numpy_bytes.reshape(frame_event.FrameHeight, frame_event.FrameWidth, 4)
                        cv2.imshow('Grabbed', newarr)
                        # Check for keyboard inputs indicating that the user wants to quit by pressing the q key
                        key = cv2.waitKey(1) & 0xFF
                        if key == ord('q'):
                            break
                    case Process.GetData:
                        continue

        
        
            except KeyboardInterrupt:
                break
        # Clean up
        cv2.destroyAllWindows()
        # This ends the background thread
        self.stopStreaming()
        self.disconnect()

# Arguments: 
    # IPAddress : String
    # Palette : Enum
    # Process :Enum
def grabFrame(IPAddress, palette, process):
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
    connection.connectDevice(IPAddress)
    if connection._connectedDevice is not None:
        print("Connection Success")
        
    # Grab Frames
    frameGrabber = FrameGrabber(connection._connectedDevice)
    frameGrabber.setColorPalette(palette)
    frameGrabber.processFrame(0)
    return
    
    

if __name__ == "__main__":
    grabFrame("10.1.10.102", Palette.Palette1, Process.Show)
