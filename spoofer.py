import yaml # needed to read config files
from yaml.loader import SafeLoader # needed for loader

import random # needed to generate random values
import string # needed to access string lists of digits, letters, and hex
import time # needed for sleep

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

        # set up network interface
        self.nicSetup(nic, reservedChannels)

        # generate targets
        self.decoyGenerator(targetCount)


    def nicSetup(self, nicName, reservedChannels):
        """
        Method to setup the network interface

        Args:
            nicName (str): the name of the network interface to use
            reservedChannels (list): the list of channels to not transmit on
        """

        # TODO network setup stuff and build list of what channels the network interface can transmit on

        possibleChannels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

        # create the list of valid channels
        self.validChannels = []

        for channel in possibleChannels:
            if not channel in reservedChannels: # if the current channel is not in the reserve list, add it as a valid channel
                self.validChannels.append(channel)


    def decoyGenerator(self, targetCount):
        """
        Method to create all the decoys

        Args:
            targetCount (int): the total number of decoys to generate
        """

        self.decoyList = [] # clear out the list of decoys, if any are in there

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

            # select the channel to transmit on
            channel = random.choice(self.validChannels)

            self.decoyList.append(Decoy(mac, decoySSID, channel))

            # debug stuff:
            print(f"Decoy #{str(j)} : SSID: {decoySSID} MAC: {mac} Channel: {str(channel)}")

    def decoyLoop(self):

        while True:

            for decoy in self.decoyList:

                # for debugging
                print(f"SSID: {decoy.ssid}  MAC: {decoy.mac}  Channel: {str(decoy.channel)}")

            # for debugging
            print()
            time.sleep(1)

            # shuffle the order of all the decoys in the list after every loop
            random.shuffle(self.decoyList)
            



if __name__ == "__main__":

    print("Starting spoofer")

    configName = fd.askopenfilename(title="Select clone config file")

    with open(configName) as f:
        data = yaml.load(f, Loader=SafeLoader)
        
        startString = data['startString']
        endString = data['endString']
        addressList = data['macs']

    droneSpoofer = Spoofer(startString, endString, addressList, "TBD", [], 3)

    droneSpoofer.decoyLoop()
