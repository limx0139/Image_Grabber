
import sys

import cv2

from stream import streamWithFocusAdjust
from connectionHandler import ConnectionHandler
import ametekframegrabber as fg


def main():
    """
    Main entry point.
    """
    # Get the IP address from command line argument
    # With an IP address of 0 the first compatible camera will be chosen
    ip = "10.1.10.102"
    profile = 0
    if len(sys.argv) >= 2:
       ip = sys.argv[1]
    else:
        raise Exception("InputError: Expected IPaddress.")

    
   
    client = None
    
    try:
      client = ConnectionHandler(ip)

    except Exception as ex:
        raise ex
    client.changeProfile(profile)
    
    client = ConnectionHandler(ip)
    streamWithFocusAdjust(client._Device)



if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(ex)