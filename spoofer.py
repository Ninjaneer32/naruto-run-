import yaml # needed to read config files
from yaml.loader import SafeLoader # needed for loader
import random # needed to generate random values
import string # needed to access string lists of digits, letters, and hex
from tkinter import filedialog as fd # needed to simplify file selection


class Decoy:

    def __init__(self, mac, ssid, channel):
        """
        Initialization method for decoys

        Args:
            mac (str): The MAC address for the decoy to use as a string
            ssid (str): The SSID for the decoy to use as a string
            channel (int): The wifi channel for the decoy to transmit on.  
        """

        self.mac = mac
        self.channel = channel
        self.ssid = ssid


class Spoofer:

    def __init__(self, startString, endString, macList, nic, reservedChannels, targetCount):
        """
        Initialization method for the spoofer

        Args:
            startString (str): The static string all the decoys will start with
            endString (str): The key for generating the dynamic part of the decoys SSIDs
            macList (list): List of MAC blocks to use when creating the MAC of each decoy
            nic (str): The name of the network adapter to transmit on
            reservedChannels (list): The list of wifi channels to not transmit on and leave open
            targetCount (int): the number of decoys to generate
        """
        
        self.ssidStatic = startString
        self.ssidDynamic = endString
        self.macList = macList
        self.transmitter = nic
        self.reservedChannels = reservedChannels
        self.targetCount = targetCount

    def decoyGenerator(self, targetCount):
        """
        Method to create all the decoys

        Args:
            targetCount (int): the total number of decoys to generate
        """

        for j in range(targetCount):

            # generate SSID
            decoySSID = self.ssidStatic
            for i in self.ssidDynamic:
                if str(i).upper() == 'L': # generate random letter
                    decoySSID = decoySSID + random.choice(string.ascii_uppercase)
                elif str(i).upper() == 'N': # generate random number
                    decoySSID = decoySSID + random.choice(string.digits)
                elif str(i).upper() == 'H': # generate random hex character
                    decoySSID = decoySSID + random.choice(string.hexdigits.upper())
                elif str(i).upper() == 'A': # generate random alphanumeric character
                    decoySSID = decoySSID + random.choice(string.ascii_uppercase + string.digits)
                else:
                    decoySSID = decoySSID + str(i)

            # generate MAC address
            mac = random.choice(self.macList) # get base value from block list

            while len(mac) < 12: # keep adding hex characters until we get to a valid mac address
                mac = mac + random.choice(string.hexdigits.upper())

            # TODO add in channel selection

            # debug stuff:
            print(f"Decoy #{str(j)} : SSID: {decoySSID} MAC: {mac}")




if __name__ == "__main__":

    print("Starting spoofer")

    configName = fd.askopenfilename(title="Select clone config file")

    with open(configName) as f:
        data = yaml.load(f, Loader=SafeLoader)
        
        startString = data['startString']
        endString = data['endString']
        addressList = data['macs']

    droneSpoofer = Spoofer(startString, endString, addressList, "TBD", "TBD", "TBD")

    droneSpoofer.decoyGenerator(10)
