# Image Grabber

This is a Python script used to extract the thermal frame data from Ametek thermal cameras using the LandImagerSDK. Essential classes concerning device connection and thermal frame data are implemented in Python, abstracting away from the original C# implementation of the SDK (albeit at some cost to performance). 

## Dependencies

Versions provided are ones used to write the script. Other versions may also work. LandImagerSDK.dll assembly SDK provided by Ametek
| Dependency        | Version | 
| --------          | ------- | 
| Python            | v3.14.6 | 
| pythonnet         | 3.10    |
| numpy             | 2.4.6   |
| cv2               | 4.13.0  |
| LandImagerSDK.dll | nil     |

## Installation


```bash
pip install pythonnet
```
The LandImagerSDK.dll should be provided by the Ametek LAND SDK. This assumes a suitable version of Python, numpy and cv2 are also installed.

## Usage
Ensure all dependencies are installed and the 'LandImagerSDK.dll' file is in the working directory.
While there are a variety of different ways to import the package to your python project, by far, the most straightforward way to do so is to have the sourcecode 'ametekframegrabber.py' and the assembly SDK 'LandImagerSDL.dll' in your working directory. This will allow the script to be accessible to the python intepreter, allowing direct access to the script by calling the following import:
```python
import amatekframegrabber as lfg
```
### Connect Function
```python
# returns a connection to the camera at the specified IPAddress (string) if available
# The returned object is used directly to instantiate a Device Class object
# returns None if no camera is found at the specified IPAddress
    # Under the hood, this instantiates a Discovery class that finds the camera, 
    # which then falls out of scope within the function call.
connectedDevice = lfg.connect(IPAddress)
```

### Device Class
A device class object is used to connect to the camera. This is functionally a boiled down version of DeviceAPI in the SDK documentation, with functions for connection, streaming, and capturing thermal data ported over to Python.
```python
# Constructor
    # Instantiates the DeviceAPI for that device found using lfg.connect function
    # returns None if connectedDevice is invalid
    Device = lfg.Device(connectedDevice)

# Parameters
    # DeviceAPI for selected device
    Device._connectedDevice = DeviceAPI
    # Threading lock (mutex) to sync the frame grabbing and image processing threads
    Device._frame_event_lock    = threading.Lock()
    # Variable to store the ThermalFrame for processings
    Device._frame_event         = None
    # Event to alert listening functions whenever a Thermal Frame is available
    Device._frame_availale = threading.Event()

# Functions
    # Choose a colour pallate. 
    # Argument is a enum defined within the script
    Device.setColorPalette(lfg.Pallate)

    # Starts the camera
    # Starts a background thread receiving Thermal Frames. 
    Device.startStreaming()

    # Stops the camera
    # Stops the background thread listening to the camera
    Device.stopStreaming()

    # Disconnects the Device from the camera
    # Ensure this function is called once camera is no longer needed to avoid memory leakage.
    disconnect()

```
### Thermal Frame Class
A Thermal Frame class object is used to store pertinent thermal frame information. This ports the thermal frame class in the C# SDK over to Python. Construct this class to convert the C# ThermalFrame class to a equivalent Python class. This is done on the main thread for optimisation purposes.

This class contains all the information extracted from each frame of the camera, and exposes it to be processed using python.

```python
# Constructor
    # Creates a copy of the thermal frame provided by the Device Class for image processing
    # The argument is a reference to a C# class produced by the assembly dll.
    # This function converts the C# class into a python operatable version
    frame = fg.ThermalFrame(Device._frame_event)

# Parameters
    # Contains a copy of the original C# Thermal Frame Class
    frame._frame = ThermalFrame
    frame._backgroundTemp = ThermalFrame.BackgroundTemp
    frame._emissivity = ThermalFrame.Emissivity
    frame._height = ThermalFrame.FrameHeight
    frame._width = ThermalFrame.FrameWidth
    frame._minTemp = ThermalFrame.MinTemp
    # Stores the (x,y) coordinates where minimum temperature occurs as a 2-tuple
    frame._minIndex = divmod(ThermalFrame.MinIndex, frame._width)[::-1]
    frame._maxTemp = ThermalFrame.MaxTemp
    # Stores the (x,y) coordinates where maximum temperature occurs as a 2-tuple
    frame._maxIndex = divmod(ThermalFrame.MaxIndex, frame._width)[::-1]
    # Stores a 2D np array containing temperature data of each pixel of the frame
    frame._tempData = np.frombuffer(ThermalFrame.TemperatureData, dtype=np.float32).reshape(frame._height, frame._width, 1)
    # Stores a np array containing colour data of each pixel of the frame
    # Each pixel is stored as a 4 unsigned 8-bit integers, i.e. the format is B8G8R8A8, that is, data is stored in order, Blue, Green, Red, Alpha, as 8-bit unsigned integers, with 0-255 representing intensity.
    frame._image = np.frombuffer(bytes(ThermalFrame.GetTemperatureBitmap().PixelData), dtype=np.uint8).reshape(frame._height, frame._width, 4)


# Functions
    # Returns a copy of the thermal frame
    copiedFrame = frame.clone()

```


### Example Functions
Here are some premade example functions provided to be called directed from the sourcecode:

```python
# Show the camera display of a connected camera.
    # Calls startStream, listens in on the background thread and displays a window using cv2
    # Then waits for the keyboard input 'q' to terminate.
    # Calls stopStream and cleans up resources afterwards.
showFrames(Device)

# Given an IPAddress and colour palette, call showFrames for the camera associated (if it exists) with the chosen colour pallete
# The palettes follow the implementation in the SDK, ported over as Python Enums.
# This function is a combination of lfg.connect and showFrames, with the endpoints connected as is appropriate
streamFrame(IPAddress, palette)
```
## Notes on threading
This script uses a background thread to receive thermal frames from the camera API. This is necessary as the camera API itself uses a background thread to run the camera, hence, the script integrates said background thread to receive the necessary information. As such, errors will be prone to occur if the threads are not properly synced. In the example code provided, an instance of proper thread syncing is shown.

## Example code
An example, in example1, is provided showing how to use to API to connect a camera at port 10.1.10.102, and access its thermal frames to draw the coordinates of maximum and minimum temperature. The area of code where each thermal frame is available to be manipulated and saved is indicated.

## Contributing


## License

