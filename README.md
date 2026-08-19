# Image Grabber with Geometry Measurements and Settings

This is a Python script used to extract the thermal frame data from Ametek thermal cameras using the LandImagerSDK. Essential classes concerning device connection and thermal frame data are implemented in Python, abstracting away from the original C# implementation of the SDK (albeit probably at some cost to performance). The Geometry directory contains the scripts to run geometry measurements, opcua logging, and csv dumping and the Settings directory contains scripts to change the mode(Profile), colour palette and focus of the camera. The barebones package containing only the python port of the LandImagerSDK is contained in the lib directory. Currently, scripts are run on the command line, though a GUI may be in the works. To run the scripts, navigate to the directories the scripts are located in and run them with the appropriate arguments. For example, to change the Profile of a camera, navigate to the Settings directory and run:
```bash
python changeProfile "yourCameraIPAddress" profileNumber
```
Details on script arguments can be found later in the documentation.

This program is written for Windows and while the python scripts may work for other platforms, some other aspects may not port over as easily.


# Contents
 - [Dependencies](#dependencies) 
 - [Base Image Grabber Documentation](#base-image-grabber-usage) 
 - [Geometry Measurer Usage](#geometry-measurer-usage)
 - [Troubleshooting](#troubleshooting)
 - [Settings Usage](#settings-usage)


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

Versions provided are ones used to write the script. Other versions may also work if they are updated. 
| Dependency        | Version | 
| --------          | ------- | 
| Python            | v3.14.6 | 
| pythonnet         | 3.10    |
| numpy             | 2.4.6   |
| cv2               | 4.13.0  |
| asyncua           | 2.0.1   |
| LandImagerSDK.dll | nil     |

If running on a virtual environment, installation commands should be run within the virtual environment. It is also possible to install all dependencies under the main python path, in which case, the dependencies are just installed, skipping the instructions for setting up virtual environments.
```bash
python -m pip install pythonnet numpy cv2 
```
The LandImagerSDK.dll can be found on the [Official Ametek website](https://www.ametek-land.com/products/software/imagersdk), though it is also included in this repository. As per the specifications on the official LandImagerSDK documentation, this file needs to be in the base directory for any program with it as a dependency. e.g. Settings has the LandImagerSDK.dll within its directory. 



## Image Grabber Documentation
The image grabber can be accessed through the amatekframegrabber.py API, which is fundamentally a python port of the LandImagerSDK.dll. 
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

# A port for the proprietory response codes used by the LandImagerSDK. Most functions sending instructions and receiving information to a camera receive a response object containing a value and a response code indicating the result of the function. This enum ports the response code enum class to python. This functionality is ported over to python by allowing functions to throw exceptions indicating the type of response code, if not success. 
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

    # Returns the current active profile of the camera
    getActiveProfile()

    # Returns the number of profiles the camera supports
    getProfileCount()

    # Changes the current profile of the camera to the one pointed at the index argument
    # This disconnects the camera as the camera reboots, and destroys the Device object.
    # So it is necessary to reconnect the camera and reinstate a Device object afterwards.
    setActiveProfile()

    # Returns a list of camera profiles associated with the Device connected.
    getProfileCount()

    # Returns the temperature range of the current profile of the current temperature as an array.
    getTemperatureRange()

    # Adjusts the focus of the camera.
    # lfg.FocusAdjustment: Enum lfg.FocusAdjustment
        # FocusAdjustment.MoveIn - Moves focus in
        # FocusAdjustment.MoveOut - Moves focus out
        # FocusAdjustment.SetToValue - Sets focus to the values specified in position
    # position: int
    # N.B. Some cameras, including the LWIR-640, do not support the SetToValue option and will fail silently.
    adjustFocus(lfg.FocusAdjustment, position)

    # Returns the current focus position of the camera.
    # N.B. Some cameras, including the LWIR-640, do not support this operation, and will return a Success-0 Response
    getFocusPosition()

    # Use autofocusing native to the camera to focus the object at the input distance.
    # distance: distance to object in metres
    #N.B. This operation is not supported by the LWIR-640, which will return a Not Supported Execption
    setAutoTargetFocus(distance)


```
### Thermal Frame Class
A Thermal Frame class object is used to store pertinent thermal frame information. This ports the thermal frame class in the C# SDK over to Python. Construct this class to convert the C# ThermalFrame class to a equivalent Python class.

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

### Response Class

The response class ports the proprietory response class implemented in the SDK. This contains a value an a Reponse Code Enum. This class should not be interacted with normally as responses are automatically converted to python exceptions when the response codes are not success.



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
The scripts in the Geometry folder build a program used to measure the lengths at various Regions of Interes(ROIs) of a hot object assumed to be roughly parallel to the plane of the camera, broadcasting this information as a OPCUA server and logging the information in a csv dump file located in \Geometry\logs. Video Recording and screengrabbing features are also implemented.

### Quick Start
The script runs out of the box with the main.py function, which handles the main working thread of the program. Ensure all dependencies are installed, navigate to the Geometry directory and run main.py:
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
<img src="documentation\NormalFrame.png " alt="Default Window" width="1000"/>
</p>

Two windows, one showing vertical ROIs and the other showing horizontal ROIs are plotted. Note the locations of the ROIs as well as the overlay.  

Also, note the terminal log:

<p align="center">
<img src="documentation\NormalTerminal.png " alt="Default Terminal" width="1000"/>
</p>

Under normal conditions, the only continuous logs on the terminal should be the server and camera frames per second. If any angry looking error messages pop up, it is likely something has gone wrong in the background, in which case, refer to the [Troubleshooting section](#troubleshooting) section. Even if the camera boots up without issue, errors logged may indicate problems with helper threads, e.g. the OPCUA server may have crashed.

Further note that in the above example, the camera is unfocused and directed at empty space, so the it is only displaying the ambient temperature. To view the expected output during forging, run the analyseVideo.py file in the same directory. 
```python
python analyseVideo.py
```
<p align="center">
<img src="documentation\AnalyseVideoExample.png " alt="Example Output" width="600"/>
</p>

You can also add an additional argument to the AnalyseVideo.py script to point to a video file to analyse:

```python
python analyseVideo.py relative\path\to\video
```

### Run with parameters
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

Below are the relevant parameters for forging: 

<p align="center">
<img src="documentation\GlobalParametersDefaults.png " alt="Global Parameters Defaults" width="600"/>
</p>

| Parameter            | Description                                    | 
| --------             | -------                                        | 
| IP_ADDRESS           | IP Address of the camera                       |
| SERVER_ENDPOINT      | Endpoint for the OPCUA Server                  |  
| NUM_VERTICAL_ROIS    | Number of Vertical ROIs                        | 
| NUM_HORIZONTAL_ROIS  | Number of Horizontal ROIs                      | 
| CHOSEN_UNITS         | Unit of measurement                            | 
| PIXEL_CONVERSION_RATE| number of said unit per pixel                  |  
| MAKE_LOGS            | Whether to log data as csv/image dump          |  
| CANNY_SIGMA          | Canny Algorithm Wideness                       |  
| GAUSSIAN_BLUR_INDEX  | Degree of Blur for Canny Algorithm (Odd Int)   | 
| REFLECTIVE_INDEX     | Expected reflectivity of background material   |
| SENSITIVITY          | Temperature difference to detect objects       | 



Command line settings take precedence and will override the settings in \Geometry\scripts\globalParameters.

### Features
The Geometry Measurer comes with baseline features, those requiring user input during running are indicated on the screen overlay:


<p align="center">
<img src="documentation\FeaturesOverlay.png " alt="Features Overlay" width="600"/>
</p>

These indicate the keyboard inputs the program listens to as it is running.
Overlay:
- Current Time
- Whether video recording is on
- input s to save current frame
- input t to start recording temperature data
- input r to start recording video
- input y to stop recording
- input q to quit program

The visual overlay can also be turned off by toggling the SHOW_OVERLAY option in Geometry\scripts\globalParameters.py

#### Screenshots
The program listens to the input so save the current frame as a screenshot. Each screenshot saves 2 frames, the horizontalROI and verticalROI frames with annotation are saved separately. 
Manually taken screenshots are saved in the Geometry/logs/images/manual folder.

#### Video Recording
The program listens to inputs, t, r and y to manage video recording while running.
Only one video output, temperature data or video data is permitted at one time. In order to switch over to the other output, the current recording has to be terminated. Both recordings use cv2's default AVI format for minimal data loss, so, especially with temperature data, the frame data can be reconstructed at a later date for processing. Recording video data records the the 'Vertical ROIs' frame data, which includes the annotations for the the ROIs and the overlay. As cv2 does not allow variable frame rate, the framerates on the produced video files may be inaccurate. This should not be an issue if the purpose of recording data is to load it back in to cv2 (temperature data is recommended as it is lossless) for post processing.

Videos are timestamped in the name and saved in the Geometry/logs/videos folder:

<p align="center">
<img src="documentation\VideoLocation.png " alt="Video Location" width="600"/>
</p>

### OPCUA Server
The program also runs an OPCUA server in the background to broadcast ROI data. By default, the server endpoint is '0.0.0.0:5555' or 'localhost:5555' (both indicate localhost), though changing the endpoint accordingly to run on ethernet or internet is possible. The port 5555 is used as the default OPCUA server port 4840 on the AFRC device is busy. 
The server has no security and communicates anonymously. It can be connected accordingly on UAExpert:

<p align="center">
<img src="documentation\OPCUAServerDiscovery.png " alt="OPCUA Server" width="600"/>
</p>

Once connected, the locations on the OPCUA Server are now accessable:

<p align="center">
<img src="documentation\OPCUAConnectedServer.png " alt="OPCUA Locations" width="600"/>
</p>

ROI data is updated on the horizontal and vertical GeometryObject nodes, of which the units used is located in unitObject node. 

<p align="center">
<img src="documentation\ServerUnitLoc.png " alt="Server Unit Location" width="600"/>
</p>

<p align="center">
<img src="documentation\ServerROILoc.png " alt="Server ROI Location" width="600"/>
</p>

Note that in the above example, the unitObject is pixels, which is the default, and the value stored in the node horizontalROI1, corresponding to the upper most horizontalROI, is 0, because the camera is not pointed at anything notable.

Connecting the OPCUA server sometimes results in a noticable drop in framerate.

<p align="center">
<img src="documentation\PerformanceImpactofServerConnection.png " alt="Server FPS Drop" width="600"/>
</p>

### Logging

Datalogging is enabled by default, though this setting can be changed by changing the MAKE_LOGS parameter in the globalParameters.py file, to False.

<p align="center">
<img src="documentation\TurnOffLogging.png " alt="Turn off Logging" width="600"/>
</p>

Each time main.py is run, a single csv file is generated containing the horizontal and vertical ROI data for every frame, timestamped to the microsecond. The log file is found in Geometery\logs and is itself automatically timestamped to in its name.

<p align="center">
<img src="documentation\csvLogLoc.png " alt="Log location and timestamp" width="600"/>
</p>

Images are also automatically logged every 60 frames, which at around 35-50 frames per second is about a frame every 1-2 seconds. 2 images are processed at each time, and they are saved in Geometery\logs\images.


<p align="center">
<img src="documentation\Images_Log.png " alt="Image path location" width="600"/>
</p>

## Troubleshooting

### System.NotSupportedException: LandImagerSDK.dll Blocked 

An error may occur when the any software using ametekframegrabber.py is run on first installation:

```bash
System.NotSupportedException: An attempt was made to load an assembly from a network location which would have caused the assembly to be sandboxed in previous versions of the .NET Framework. This release of the .NET Framework does not enable CAS policy by default, so this load may be dangerous. If this load is not intended to sandbox the assembly, please enable the loadFromRemoteSources switch. See http://go.microsoft.com/fwlink/?LinkId=155569 for more information.

```

This error occurs when attempting to load a dll file windows does not trust. In this case, the LandImagerSDK.dll is blocked by windows. To fix this error, first ensure that LandImagerSDK.dll is legitimate, by downloading it from the official Ametek website. Then, manually unblock the LandImagerSDK.dll file referenced:

- Find the LandImagerSDK.dll file referenced
<p align="center">
<img src="documentation\AllowLandImagerSDK_1.png " alt="Find LandImagerSDK" width="600"/>
</p>

- Select properties

<p align="center">
<img src="documentation\AllowLandImagerSDK_2.png " alt="Find LandImagerSDK" width="600"/>
</p>

- Check the option to unblock the dll file.

<p align="center">
<img src="documentation\AllowLandImagerSDK_3.png " alt="Find LandImagerSDK" width="600"/>
</p>

- Apply changes.

<p align="center">
<img src="documentation\AllowLandImagerSDK_4.png " alt="Find LandImagerSDK" width="600"/>
</p>

### PermissionError: : Port Busy causes OPCUA server to crash

Assigning a port that is busy for the OPCUA server causes it to crash, while the rest of the program functions relatively unaffected. This error can be seen in the command line log as such:
```bash
------------Current Settings------------
#Settings log
...
----------------------------------------
#Error log
...
...
...
PermissionError: [Errno 13] error while attempting to bind on address ('0.0.0.0', 4840): [winerror 10013] an attempt was made to access a socket in a way forbidden by its access permissions

# Main thread logs
...
```

This is caused by the OPCUA attempting to access a port that is busy. In this case, the default port for OPCUA servers, 4840, is busy, likely running another OPCUA server. To fix this, change the port for the OPCUA server to one that is available. The default port assigned in globalParameters is 5555.

<p align="center">
<img src="documentation\OPCUA_Default_Port.png " alt="OPCUA Default Port" width="600"/>
</p>

As the OPCUA server runs on a separate thread, this error will occur undetected by the main thread.

## Settings Usage
The scripts in the Settings folder allow for changing the base settings of the Ametek camera connected. Ensure the working directory is ...\Settings\ to run these scripts.

```bash
(venv) C:\Users\Administrator\Documents\geometryMeasurementSourceCode\Image_Grabber-main\Geometry>cd path\to\Settings

(venv) C:\Users\Administrator\Documents\geometryMeasurementSourceCode\Image_Grabber-main\Settings>
```




### Change Palette

changePalette.py changes the colour palette of the camera. The script takes the camera IP address and a numerical input to determine the palette to be changed to:

| Input    | Palette                                    | 
| -------- | -------                                    | 
| 1        | Grayscale color palette                    |
| 2        | Blue to yellow palette. Default palette.   |  
| 3        | Purple to yellow palette                   | 
| 4        | Red to yellow palette.                     | 
| 5        | High contrast palette.                     | 


The following command changes the colour palette to grayscale:
```bash
python changePalette.py 10.1.10.102 1
```
<p align="center">
<img src="documentation\ChangeProfile_Gray.png " alt="Find LandImagerSDK" width="600"/>
</p>

### Change Palette

changeProfile.py changes the Profile of the camera, which contains the camera's temperature range mode. Different cameras have different profiles so running changeProfile also lists the available options for the camera. This script also accepts as arguments, the IP address of the camera and the profile to be changed to encoded as a number.

The following command changes the profile of the camera at IP Address 10.1.10.102 to the first option:

```bash
python changeProfile.py 10.1.10.102 1
```
<p align="center">
<img src="documentation\Change_Profile.png " alt="Find LandImagerSDK" width="600"/>
</p>

Note that the command logs the options for the camera's profile and the numerical encoding for each of them. The above command changes the temperature range to 100-1000 degrees C, and for example, to change the temperature range to -20-120, the following command should be run:

```bash
python changeProfile.py 10.1.10.102 11
```
### Focusing

tuneFocus.py allows the camera's focus to be tuned. Run tuneFocus with the IP Address of the camera to be tuned as an argument:

```bash
python tuneFocus.py 10.1.10.102
```
<p align="center">
<img src="documentation\Tune_Focus.png " alt="Find LandImagerSDK" width="600"/>
</p>

This opens a window displaying the camera output and an overlay detailing the key presses the program is listening to:
- 'i': Move focus in
- 'o': Move focus out
- 'q': Quit Program

## Development

The sourcecode in this repository may be used freely to support development of applications using the LandImagerSDK.dll.


## Contributing


## License

