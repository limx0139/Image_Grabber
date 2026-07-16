
import sys

from Settings import stream
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
    if len(sys.argv) >= 3:
       ip = sys.argv[1]
       profile = sys.argv[1]

    
   
    client = None
    
    try:
      client = ConnectionHandler(ip)

    except Exception as ex:
        print(ex)
        return
    client.changeProfile(profile)
    
    client = ConnectionHandler(ip)
    stream(client._Device)



if __name__ == "__main__":
    main()