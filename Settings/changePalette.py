# Connects to the camera and directly streams it using cv2
# Choose from 5 colour palettes
import sys

from scripts.ametekframegrabber import Device, Palette, connect, showFrames


def changePalette(IPAddress, palette):
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

if __name__ == "__main__":
    palette = Palette.Palette1
    if len(sys.argv) >= 2:
       palette = int(sys.argv[1])
    match palette:
        case 1:
            palette = Palette.Palette1
        case 2: 
            palette = Palette.Palette2
        case 3:
            palette = Palette.Palette3
        case 4:
            palette = Palette.Palette4
        case 5:
            palette = Palette.Palette5
        case _:
            raise Exception('InputError: no palette corresponding to input found.')
    changePalette("10.1.10.102", palette)