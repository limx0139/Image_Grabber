
import ametekframegrabber as fg

class SettingsHandler:

    def __init__(self, ipAddress):
        # Initialises connection with camera
        try:
            
            self._ipAddress = ipAddress
            self._connectedDevice = fg.connect(ipAddress)
            self._Device = fg.Device(self._connectedDevice)

        except Exception as ex:
            raise ex

    def changeProfile(self, profile):
        """
        Changes Camera Profile
        """
        self._Device.setActiveProfile(profile)
        self._Device.disconnect()
    
    def getCurrentProfileName(self):
        index = self._Device.getActiveProfile()
        return self._Device.getProfileNames()[index]
    
    def getProfileNames(self):
        return self._Device.getProfileNames()