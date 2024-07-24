import yaml # needed to read config files
from yaml.loader import SafeLoader # needed for loader

import random # needed to generate random values
import string # needed to access string lists of digits, letters, and hex
import time # needed for sleep

import os # needed to run commands
import sys # needed for system
import subprocess # needed for subprocess calls

from scapy.all import * # needed for writing the packets
from threading import Thread # needed for multithreading

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

    def toString(self):
        return f"{self.ssid} {str(self.channel)} {self.mac}"


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
        self.nicSetup(reservedChannels)

        # generate targets
        self.decoyGenerator(targetCount)

    def setupInterface(self):
        ''' Puts the interface into monitor mode '''

        print(f"Placing {self.transmitter} into monitor mode")
        os.system('ifconfig ' + self.transmitter + ' down')
        try:
            os.system('iwconfig ' + self.transmitter + ' mode monitor')
        except:
            print("Failed to setup monitor mode")
            return False

        os.system('ifconfig ' + self.transmitter + ' up')
        
        return True

    def nicSetup(self, reservedChannels):
        """
        Method to setup the network interface

        Args:
            reservedChannels (list): the list of channels to not transmit on
        """

        self.setupInterface()

        channelText = subprocess.run(['iwlist', str(self.transmitter) ,'freq'], capture_output=True, text=True).stdout
        
        # start with classic 2.4GHz Channels
        possibleChannels = {'01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13'}
        for line in channelText.splitlines():
            #print(line)
            if "Channel" in line and "Current" not in line:
                possibleChannels.add(line.split()[1])

        # create the list of valid channels
        self.validChannels = []

        if len(reservedChannels) > 0: # reserved list is not empty
            for channel in possibleChannels:
                if channel in reservedChannels: # if the current channel is in the reserve list, add it as a valid channel
                    self.validChannels.append(channel)
        else:
            for channel in possibleChannels:
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

            # add ':' to mac
            mac = mac.lower()
            temp = ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))
            mac = temp

            # select the channel to transmit on
            channel = random.choice(self.validChannels)

            self.decoyList.append(Decoy(mac, decoySSID, channel))

            # debug stuff:
            #print(f"Decoy #{str(j)} : SSID: {decoySSID} MAC: {mac} Channel: {str(channel)}")

    def printStatus(self):
        """
        prints status of the spoofer to console
        """

        print(f"\nUsing {self.transmitter} with the following possible transmission channels:")
        print(f"{str(self.validChannels)}")
        print()
        print(f"Running {str(len(self.decoyList))} decoy targets")

        for decoy in self.decoyList:
            print(decoy.toString())
        print()

    def decoyLoop(self):

        while True:

            for decoy in self.decoyList:

                # for debugging
                #print(f"SSID: {decoy.ssid}  MAC: {decoy.mac}  Channel: {str(decoy.channel)}")

                os.system(f"iwconfig {self.transmitter} channel {decoy.channel}")
                #os.system(f"iwconfig {self.transmitter} channel 01")

                time.sleep(1)

                dot11 = Dot11(type=0, subtype=8, addr1='ff:ff:ff:ff:ff:ff', addr2=decoy.mac, addr3=decoy.mac)
                beacon = Dot11Beacon()
                essid = Dot11Elt(ID='SSID',info=decoy.ssid, len=len(decoy.ssid))
                rsn_array = [b'\x01\x00',
                b'\x00\x0f\xac\x04',
                b'\x02\x00',
                b'\x00\x0f\xac\x04',
                b'\x00\x0f\xac\x02',
                b'\x01\x00',
                b'\x00\x0f\xac\x02',
                b'\x00\x00']
                rsn_bytes = b''.join(rsn_array)
                rsn = Dot11Elt(ID='RSNinfo', info=rsn_bytes, len=len(rsn_bytes))

                frame = RadioTap()/dot11/beacon/essid/rsn

                sendp(frame, iface=self.transmitter, verbose=0)

            # for debugging
            #print()
            #time.sleep(1)

            # shuffle the order of all the decoys in the list after every loop
            random.shuffle(self.decoyList)
            



if __name__ == "__main__":

    print("Starting spoofer")

    interfaceList = []
    results = subprocess.run(['iwconfig'], shell=True, capture_output=True, text=True)

    for line in results.stdout.splitlines():

        if not line.startswith(" "): # check to see if its the string with the interface name

            firstWord = line.split()[0]
            interfaceList.append(firstWord)

    print("\nAvailable Interfaces:")
    for i in range(len(interfaceList)):
        print(f"{str(i)} : {interfaceList[i]}")

    interfaceNum = input("Enter the number associated with the interface you want to use: ")

    resrvChannelString = input("Enter the number for each of the wifi channels you do want to transmit on, space separated (leave blank for all possible): ")

    resrvList = resrvChannelString.split()

    # add 0's to make everything two digits
    for i in range(len(resrvList)):
        if len(resrvList[i]) < 2:
            resrvList[i] = '0' + resrvList[i]

    targetCount = int(input("Enter the number of decoys to generate: "))

    configName = fd.askopenfilename(title="Select clone config file")

    with open(configName) as f:
        data = yaml.load(f, Loader=SafeLoader)
        
        startString = data['startString']
        endString = data['endString']
        addressList = data['macs']

    droneSpoofer = Spoofer(startString, endString, addressList, interfaceList[int(interfaceNum)], resrvList, targetCount)

    droneSpoofer.printStatus()

    droneSpoofer.decoyLoop()
