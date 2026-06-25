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
pip install numpy
```
The LandImagerSDK.dll should be provided by the Ametek LAND SDK.

## Usage
Ensure all dependencies are installed and the 'LandImagerSDK.dll' file is in the working directory.
While there are a variety of different ways to import the package to your python project, by far, the most straightforward way to do so is to have the sourcecode 'ametekframegrabber.py' and the assembly SDK 'LandImagerSDL.dll' in your working directory. This will allow the script to be accessible to the python intepreter, allowing direct access to the script by calling the following import:
```python
import Landframegrabber as lfg
```
### Connection
```python
# returns a connection to the camera at the specified IPAddress (string) if available
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
Device = lfg.Device(connectedDevice)

# Parameters

# Functions

```
### Thermal Frame Class
A Thermal Frame class object is used to store pertinent thermal frame information. This ports the thermal frame class in the C# SDK over to Python. Construct this class to convert the C# ThermalFrame class to a equivalent Python class. This is done on the main thread for optimisation purposes.

```python
# Constructor
# Instantiates the DeviceAPI for that device found using lfg.connect function
Device = lfg.Device(connectedDevice)

# Parameters

# Functions

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

## Example code

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)
