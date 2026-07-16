
import sys

from connectionHandler import SettingsHandler
import ametekframegrabber as fg

def main():
    """
    Main entry point.
    """
    # Get the IP address from command line argument
    # With an IP address of 0 the first compatible camera will be chosen
    ip = "10.1.10.102"
    if len(sys.argv) >= 3:
       ip = sys.argv[1]
       profile = sys.argv[1]
    
   
    client = None
    
    try:
      client = SettingsHandler(ip)

    except Exception as ex:
        print(ex)
        return
    client.changeProfile(profile)



if __name__ == "__main__":
    main()