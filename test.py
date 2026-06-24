
import clr
import os
import sys

a=r"C:\Users\kpb26117\OneDrive - University of Strathclyde\Documents\Coding\LAND\Image_Grabber\LandImagerSDK.dll"

clr.AddReference(a)
clr.AddReference("System")

import LandImagerSDK as li
import System

print(li.Discovery.DiscoverDevices())

class ConnectLANDDialogue:
     
    def __init__(self):
        # Dummy initial connection
        self._connectDevice = li.Model.ConnectionInfo(System.Net.IPAddress.Parse("127.0.0.1"), System.Net.IPAddress.Parse("255.255.0.0"), 1040, li.Enums.IPMode.Static, "12345", li.Enums.ImagerModel.ARC)
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
        return
                
    
    class ConnectionItem:
        def __init__(self, connectionInfo):
            self._connectionInfo = connectionInfo
    

        def getConnectionInfo(self):
            return self._connectionInfo

        def toString(self):
            self._connectionInfo.IPAddress.ToString()
 
            

def main():
    """
    Main entry point.
    """
    connection = ConnectLANDDialogue()
    print(connection._discoveredDevices)
    connection.discoverDevices()
    print(connection._discoveredDevices)
    
    return
    
    

if __name__ == "__main__":
    main()
