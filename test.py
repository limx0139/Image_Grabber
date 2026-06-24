import clr
import os

a=r"C:\Users\kpb26117\OneDrive - University of Strathclyde\Documents\Coding\LAND\Image_Grabber\LandImagerSDK.dll"

clr.AddReference(a)

import LandImagerSDK as li

print(li.Discovery.DiscoverDevices())


def main():
    """
    Main entry point.
    """
    video_path = "video4.mp4"
    analyser = AnalyseVideo()
    analyser.loadVideo(video_path)
    
    

if __name__ == "__main__":
    main()
