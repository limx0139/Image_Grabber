# Image Grabber with Geometry Measurements and Settings

This is a Python script used to extract the thermal frame data from Ametek thermal cameras using the LandImagerSDK. Essential classes concerning device connection and thermal frame data are implemented in Python, abstracting away from the original C# implementation of the SDK (albeit probably at some cost to performance). The Geometry directory contains the scripts to run geometry measurements, opcua logging, and csv dumping and the Settings directory contains scripts to change the mode(Profile), colour palette and focus of the camera. The barebones package containing only the python port of the LandImagerSDK is contained in the lib directory. Currently, scripts are run on the command line, though a GUI may be in the works. To run the scripts, navigate to the directories the scripts are located in and run them with the appropriate arguments. For example, to change the Profile of a camera, navigate to the Settings directory and run:
```bash
python changeProfile "yourCameraIPAddress" profileNumber
```
Details on script arguments can be found later in the documentation.

This program is written for Windows and while the python scripts may work for other platforms, some other aspects may not port over as easily.


# Contents
 - [Dependencies](#dependencies) 
 - [Base Image Grabber Usage](#base-image-grabber-usage) 
 - [Base Image Grabber Usage](#base-image-grabber-usage) 

## Dependencies

### Using a Virtual Environment
It is recommended to use virtual environments with python dependencies to prevent issues down the line with conflicting python packages. The [Official Python Documentation](https://docs.python.org/3/library/venv.html) has all the information on virtual environments and how to set them up, but all we need to know is to run the following commands in the main directory of this repository:


```bash
# Create a virtual environment in the current directory in the folder 'venv'
python -m venv venv
# activate the virtual environment
venv\scripts\activate
```
Afterwards, your command line should look like this:
```bash
(venv) \path\to\current\directory>
```
To deactivate the virtual environment, run the following command:

```bash
deactivate
```

A virtual environment has been created in the remote desktop at AFRC future forge with the appropriate dependencies installed in the folder:
```bash
C:\Users\Administrator\Documents\geometryMeasurementSourceCode\Image_Grabber-main\
```
To remove a virtual environment, simply delete the virtual environment directory.



### Installation

Versions provided are ones used to write the script. Other versions may also work. LandImagerSDK.dll assembly SDK provided by Ametek.
| Dependency        | Version | 
| --------          | ------- | 
| Python            | v3.14.6 | 
| pythonnet         | 3.10    |
| numpy             | 2.4.6   |
| cv2               | 4.13.0  |
| matplotlib        | 3.11.0  |
| LandImagerSDK.dll | nil     |

If running on a virtual environment, installation commands should be run within the virtual environment. It is also possible to install all dependencies under the main python path, in which case, the dependencies are just installed, skipping the instructions for setting up virtual environments.
```bash
python -m pip install pythonnet numpy cv2 matplotlib
```
The LandImagerSDK.dll can be found on the [Official Ametek website](https://www.ametek-land.com/products/software/imagersdk), though it is also included in this repository. As per the specifications on the official LandImagerSDK documentation, this file needs to be in the base directory for any program with it as a dependency. e.g. Settings has the LandImagerSDK.dll within its directory. 

Depending on the security configurations of the machine running the program, the LandImagerSDK.dll may be flagged as potentially malicious as a unknown assembly dll script. To work around this, ensure that the 'LandImagerSDK.dll' is legitimate, then navigate to it in folders, right click it and select properties. ....
# TODO, make troubleshooting page



## Base Image Grabber Usage
The image grabber can be accessed through the amatekframegrabber.py API, which is itself a (albeit incomplete at the moment) python port of the LandImagerSDK.dll. 
Ensure all dependencies are installed and the 'LandImagerSDK.dll' file is in the working directory.
While there are a variety of different ways to import the package to your python project, by far, the most straightforward way to do so is to have the sourcecode 'ametekframegrabber.py' and the assembly SDK 'LandImagerSDL.dll' in your working directory. This will allow the script to be accessible to the python intepreter, allowing direct access to the script by calling the following import:
```python
import amatekframegrabber as fg
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
### Enums
Several Enum classes are packaged within the python port, mostly as a direct port from the proprietory datatypes in the LandImagerSDK itself.
```python
# The Colour palette mode used by the camera. The SDK allows for more fine tuning of the colour palette, it is likely easier to manipulate the colour bitmap directly using opencv in python.
class Palette(Enum):
    # Grayscale palette
    Palette1 = 1
    # Blue to Yellow Palette
    Palette2 = 2
    # Purple to Yellow Palette
    Palette3 = 3
    # Red to Yellow Palette
    Palette4 = 4
    # High Contrast Palette
    Palette5 = 5

# A port for the proprietory response codes used by the LandImagerSDK. Most functions sending instructions and receiving information to a camera receive a response function containing a value and a response code indicating the result of the function. This enum ports the response code enum class to python.
class ResponseCode(Enum):
    Disconnected = 1
    Error = 2
    NotSupported = 3
    Success = 4

# Instructions to send to the camera to adjust focus.
class FocusAdjustment(Enum):
    MoveIn = 1
    MoveOut = 2
    SettoValue = 3
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
    # Boolean data to indicate if the device supports profiles
    Device._supportsProfiles = bool(self._connectedDevice.SupportsProfiles)
    # If the device supports profile(modes), the following parameters will be active
        # The number of profiles the device supports
        Device._profileCount = int(self.getProfileCount())
        # The names of the profiles, stored as a array of strings
        Device._profileNames = self.getProfileNames()
        # The current profile
        Device._activeProfile = self.getActiveProfile()

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
Here are some premade example functions provided to be called directed:

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

### Example code
An example, in example1, is provided showing how to use to API to connect a camera at port 10.1.10.102, and access its thermal frames to draw the coordinates of maximum and minimum temperature. The area of code where each thermal frame is available to be manipulated and saved is indicated.


### Notes on threading
This script uses a background thread to receive thermal frames from the camera API. This is necessary as the camera API itself uses a background thread to run the camera, hence, the script integrates said background thread to receive the necessary information. As such, errors will be prone to occur if the threads are not properly synced. In the example code provided, an instance of proper thread syncing is shown.

## Geometry Measurer Usage
The scripts in the Geometry folder build a program used to measure the lengths at various Regions of Interest of a hot object assumed to be roughly parallel to the plane of the camera, broadcasting this information as a OPCUA server and logging the information in a csv dump file located in \Geometry\logs.
#### Quick Start
The script is rigged to run out of the box with the main.py function, which handles the main working thread of the program. Ensure all dependencies are installed, navigate to the Geometry directory and run main.py:
```bash
python main.py
```
This runs the Geometry measurer algorithm on default arguments:
| Argument               | Value                                    | 
| --------               | -------                                  | 
| ipAddress              | 10.1.10.102                              | 
| opcuaServerEndpoint    | opc.tcp://0.0.0.0:5555/freeopcua/server/ |
| numberOfVerticalROIs   | 20                                       |
| numberOfHorizontalROIs | 10                                       |
| pixelConversion        | 1                                        |
| units                  | Pixels                                   |

If successful, we should get the following window:

<p align="center">
<img src="documentation\DefaultWindow.png " alt="Default Window" width="600"/>
</p>

Do note that this example has the camera pointed at nothing, so the it is only displaying the ambient temperature. To view the expected output during forging, run the analyseVideo.py file in the same directory. 
```python
python analyseVideo.py
```
<p align="center">
<img src="documentation\AnalyseVideoExample.png " alt="Example Output" width="600"/>
</p>
Moreover, note the lines displaying the locations of the 10 vertical ROIs and 5 horizontal ROIs.
Ensure no errors appear on the command line, as errors may appear without the software crashing when they are raised by supporting threads. Errors may indicate the OPCUA server failing to boot. Do refer to the [Troubleshooting section](#troubleshooting) to resolve common errors.


#### Run with parameters
The program also supports running with custom parameters through the command line. 

```bash
# python main.py ipAddress opcuaServerEndpoint numberOfVerticalROIs numberOfHorizontalROIs pixelConversion units
# All arguments must be inputted in the right order, with the right type for the program to run.
# Errors will be thrown for incorrect input.
# The below example shows the parameters confligures as:
# IP Address: 10.1.10.102
# Server Endpoint: opc.tcp://0.0.0.0:5555/freeopcua/server/
# Number of Vertical ROIs: 10
# Number of Horizontal ROIs: 5
# Pixel Conversion rate: 5
# Unit measurement: MM
    # Unit measurement accepts cm, mm, pixels and will throw an error for other inputs.
python main.py 10.1.10.102 opc.tcp://0.0.0.0:5555/freeopcua/server/ 10 5 5 mm
```

Other parameters can be accessed in the file, \Geometry\scripts\globalParameters.:

<p align="center">
<img src="documentation\GlobalParametersLocation_1.png " alt="Global Parameters Location" width="600"/>
</p>

### Troubleshooting
### Development
## Settings Usage
The scripts in the Settings folder allow for changing the base settings of the Ametek camera connected.
## Contributing


## License

