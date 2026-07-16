import clr
import os
import threading
import cv2
import numpy as np
import os
from enum import Enum
from System import String, Boolean, Array, Int32, UInt32

# Finds the directory of the LandImagerSDK.dll, which should be in the same directory as the script
cwd = os.getcwd()
assemblyLocation = cwd+"\\LandImagerSDK.dll"
clr.AddReference(assemblyLocation)

# python.net Imports from clr
# Python.net is a dependency!
import LandImagerSDK as li


#ENUMS
class Palette(Enum):
    Palette1 = 1
    Palette2 = 2
    Palette3 = 3
    Palette4 = 4
    Palette5 = 5

class ResponseCode(Enum):
        
    Disconnected = 1
    Error = 2
    NotSupported = 3
    Success = 4
    
class FocusAdjustment(Enum):
    MoveIn = 1
    MoveOut = 2
    SettoValue = 3

        
    
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
            return
        # search for device with matching IPAddress
        # Assume no two devices have the same IPAddress
        connection = None
        
        for device in self._discoveredDevices:
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
 
 
# Exported (and adapted to python) DeviceAPI. 
class Device:
    def __init__(self, DeviceAPI):
        # DeviceAPI for selected device
        self._connectedDevice = DeviceAPI
        # Threading lock (mutex) to sync the frame grabbing and image processing threads
        self._frame_event_lock    = threading.Lock()
        # Variable to store the ThermalFrame for processings
        self._frame_event         = None
        # Event to alert listening functions whenever a Thermal Frame is available
        self._frame_availale = threading.Event()
        # Connect up onFrame to fire whenever the API indicates a frame is available
        if self._connectedDevice is not None:
            self._connectedDevice.ThermalFrameAvailable += self.onFrame
        else:
            raise Exception("Error: Device not Connected")
        self._supportsProfiles = bool(self._connectedDevice.SupportsProfiles)
        if self._supportsProfiles:
            self._profileCount = self.getProfileCount()
            self._profileNames = self.getProfileNames()
            self._activeProfile = self.getActiveProfile()

        
    
    def __del__(self):
        """
        Destructor.
        """
        # Ensure the client removes itself before destruction to avoid memory access issues
        if self._connectedDevice is not None:
            self._connectedDevice.Disconnect()

        
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
        if self._connectedDevice is not None:
            self._connectedDevice.ColorPalette.SelectedPalette = temp
        else:
            raise Exception("Error: Device not Connected")
        # return self._connectedDevice.ColorPalette.Palette

    def startStreaming(self):
        if self._connectedDevice is not None:
            self._connectedDevice.StartStreaming()
        else:
            raise Exception("Error: Device not Connected")
    def stopStreaming(self):
        if self._connectedDevice is not None:
            self._connectedDevice.StopStreaming()
        else:
            raise Exception("Error: Device not Connected")
    def disconnect(self):
        if self._connectedDevice is not None:
            self._connectedDevice.ThermalFrameAvailable -= self.onFrame
            self._connectedDevice.Disconnect()
        else:
            raise Exception("Error: Device not Connected")
    def onFrame(self, source, args):
        
        with self._frame_event_lock:
            # Store a copy of the event to be processed in the main thread. The provided event object is reused
            # by the SDK once the callback returns.
            self._frame_event = args.ThermalFrame.Clone()
            self._frame_availale.set()
            
        
    def getActiveProfile(self):
        if self._connectedDevice is not None:
            response = Response(self._connectedDevice.GetActiveProfile())
            Code = response._responseCode
            if Code is not ResponseCode.Success:
                raise Exception(Code)
            return response._value 
        else:
            raise Exception("Error: Device not Connected")

    def getProfileCount(self):
        if self._connectedDevice is not None:
            response = Response(self._connectedDevice.GetProfileCount())
            Code = response._responseCode
            if Code is not ResponseCode.Success:
                raise Exception(Code)
            return response._value 
        else:
            raise Exception("Error: Device not Connected")
        
    def setActiveProfile(self, profile):
        if not isinstance(profile, int):
            raise Exception("Error: Invalid Input")
        if self._connectedDevice is None:
            raise Exception("Error: Device not Connected")
        if not self._supportsProfiles:
            raise Exception("Error: Profiles not Supported on this Device")
        profileCount = self._profileCount
        if profile < 0 or profile >= profileCount:
            raise Exception("Error: Device does not Support Input Profile")
        try:
            responseCode = self._connectedDevice.SetActiveProfile(Int32(profile))
            response = Response(None)
            response.fromResponseCode(responseCode, None)
        except Exception as ex:
            raise ex
        if response._responseCode is not ResponseCode.Success:
            raise Exception(response._responseCode)



    def getProfileNames(self):
        if self._connectedDevice is not None:
            response = Response(self._connectedDevice.GetProfileNames())
            Code = response._responseCode
            if Code is not ResponseCode.Success:
                raise Exception(Code)
            result = []
            for i in range(len(response._value)):
                result.append(response._value[i])
            return result
        else:
            raise Exception("Error: Device not Connected")
        
    def getTemperatureRange(self):
        if self._connectedDevice is not None:
            temperatureRange = self._connectedDevice.GetTemperatureRange()
            result= []
            for i in range(len(temperatureRange)):
                result.append(temperatureRange[i])
            return result
        else:
            raise Exception("Error: Device not Connected")
        
    def adjustFocus(self, focusType, position):
        if self._connectedDevice is None:
            raise Exception("Error: Device not Connected")
        if not isinstance(focusType, FocusAdjustment):
            raise Exception("TypeError: 1st Argument")
        match focusType:
            case FocusAdjustment.MoveIn:
                convertedFocusType = li.Enums.FocusAdjustment.MoveIn
            case FocusAdjustment.MoveOut:
                convertedFocusType = li.Enums.FocusAdjustment.MoveOut
            case FocusAdjustment.SettoValue:
                convertedFocusType = li.Enums.FocusAdjustment.SettoValue
            case _:
                raise TypeError
        self._connectedDevice.AdjustFocus(focusType, UInt32(position))

            
        
class Response:
    def __init__(self, response):
        if response is not None:
            match response.Code:
                case li.Enums.ResponseCode.Disconnected:
                    self._responseCode = ResponseCode.Disconnected 
                case li.Enums.ResponseCode.Error:
                    self._responseCode = ResponseCode.Error 
                case li.Enums.ResponseCode.NotSupported:
                    self._responseCode = ResponseCode.NotSupported 
                case li.Enums.ResponseCode.Success:
                    self._responseCode = ResponseCode.Success 
                case _:
                    self._responseCode = None
            self._value = response.Value
    @classmethod
    def fromResponseCode(cls, responseCode, value):
        match responseCode:
            case li.Enums.ResponseCode.Disconnected:
                cls._responseCode = ResponseCode.Disconnected 
            case li.Enums.ResponseCode.Error:
                cls._responseCode = ResponseCode.Error 
            case li.Enums.ResponseCode.NotSupported:
                cls._responseCode = ResponseCode.NotSupported 
            case li.Enums.ResponseCode.Success:
                cls._responseCode = ResponseCode.Success 
            case _:
                raise TypeError
        cls._value = value




# Exported (and adapted to python) ThermalFrame. 
class ThermalFrame:
    def __init__(self, ThermalFrame):
        self._frame = ThermalFrame
        self._backgroundTemp = ThermalFrame.BackgroundTemp
        self._emissivity = ThermalFrame.Emissivity
        self._height = ThermalFrame.FrameHeight
        self._width = ThermalFrame.FrameWidth
        self._minTemp = ThermalFrame.MinTemp
        self._minIndex = divmod(ThermalFrame.MinIndex, self._width)[::-1]
        self._maxTemp = ThermalFrame.MaxTemp
        self._maxIndex = divmod(ThermalFrame.MaxIndex, self._width)[::-1]
        self._tempData = np.frombuffer(ThermalFrame.TemperatureData, dtype=np.float32).reshape(self._height, self._width, 1)
        self._image = np.frombuffer(bytes(ThermalFrame.GetTemperatureBitmap().PixelData), dtype=np.uint8).reshape(self._height, self._width, 4)
    def clone(self):
        return ThermalFrame(self)
    
    
# Functions Exported
    
# Connects to a camera given a string input of its IPAddress.
# IPAddress is generally 10.1.10.102
def connect(IPAddress):
    connection = ConnectLANDDialogue()
    connection.discoverDevices()
    if len(connection._discoveredDevices) == 0:
        raise Exception("Error: No Cameras Founds")
    connection.connectDevice(IPAddress)
    if connection._connectedDevice is not None:
        print("Connection Success")
    else:
        raise Exception("Error: Connection to Camera Failed.")
    return connection._connectedDevice

# Connects to the camera and directly streams it using cv2
# Choose from 5 colour palettes
def streamFrame(IPAddress, palette):
    """
    Main entry point.
    """
    # Connect to device
    connectedDevice = connect(IPAddress)

    # Grab Frames
    frameGrabber = Device(connectedDevice)
    frameGrabber.setColorPalette(palette)
    showFrames(frameGrabber)
    return
    
# Main Thread set up to receive frames
def showFrames(Device):
    # This starts a background thread to send the ThermalFrames from the camera
    Device.startStreaming()        
    while(True):
        # Get the latest thermal frame if there is one
        try:
            Device._frame_availale.wait()
            with Device._frame_event_lock:
                if Device._frame_event is None:
                    continue
                # Copy the thermal frame and release the resource so background thread is freed
                frame = ThermalFrame(Device._frame_event)
            cv2.imshow('Frames', frame._image)
            # Check for keyboard inputs indicating that the user wants to quit by pressing the q key
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            # Indicate that the frame has been processed and we can wait for the next frame.
            Device._frame_availale.clear()
        except KeyboardInterrupt:
            break
    # Clean up
    cv2.destroyAllWindows()
    # This ends the background thread
    Device.stopStreaming()
    # Disconnect the camera
    Device.disconnect()

if __name__ == "__main__":
    streamFrame("10.1.10.102", Palette.Palette1)
