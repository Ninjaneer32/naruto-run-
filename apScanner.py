from scapy.all import Dot11, Dot11Beacon, Dot11Elt, RadioTap, sendp, hexdump, sniff # needed for generating packet
import os # needed for OS commands
import pandas # needed for display
import time # needed for sleep
from threading import Thread, Event # needed for multithreading
import subprocess # needed for OS commands
import requests # needed for web downloads
import csv # needed to read csv files

class WifiTarget:
    ''' Class that handles the wifi targets found by the sweeper '''

    def __init__(self, bssid, ssid, dBm, ch, crypto):
        ''' init method '''

        self.maxTimeout = 3

        self.bssid = bssid
        self.ssid = ssid
        self.dBm = dBm
        self.ch = ch
        self.crypto = crypto
        self.timeOut = self.maxTimeout

        # Key used for vendor lookup
        self.key = str(self.bssid).replace(':','').upper()[0:6]
        self.vendor = "Unknown"

    def setVendor(self, vendor):
        ''' Updates the vendor '''

        self.vendor = vendor

    def updateTimeout(self, ch):
        ''' updates the timeout of the target object, \n ch: the channel currently being scanned \n Return True when timeout hits zero '''

        # if the channel being scanned is the channel the target should be on
        if ch == self.ch :
            self.timeOut = self.timeOut - 1
            
            # if the timout has been reduced to zero
            if self.timeOut <= 0 : 
                return True
            else: 
                return False
        else:
            return False

    def matchTarget(self, other):
        ''' Comapares the BSSID of two objects to see if they match '''

        if self.bssid == other.bssid : 
            
            self.ch = other.ch
            self.crypto = other.crypto
            self.ssid = other.ssid
            self.dBm = other.dBm

            self.timeOut = self.maxTimeout

            return True

        else:
            return False

class APScanner:
    ''' Class that handles the scanning of the APs '''

    def __init__(self, interface, phy):
        """
        Initializes the APScanner class

        Args:
            interface (str): the name of the interface to use
            phy (str): the physical layer associated with the interface
        """

        self.interface = interface
        self.phy = str(phy).replace("#", "")
        self.channelList = self.buildChannelList(self.phy)

        self.enableMonitorMode(self.interface)
        # initialize the networks dataframe that will contain all access points nearby
        self.networks = pandas.DataFrame(columns=["BSSID", "SSID", "Vendor", "dBm_Signal", "Channel", "Crypto"])
        # set the index BSSID (MAC address of the AP)
        self.networks.set_index("BSSID", inplace=True)

        #stop event to allow a controlled exit
        self.stopEvent = Event()

        # check to see if needed MAC list files exist
        if os.path.isfile('mam.csv') and os.path.isfile('oui.csv') and os.path.isfile('oui36.csv'):
            print('MAC list files found')
        else:
            print('MAC list files not found, downloading')
            self.downloadMACLists()

        print("Loading MAC Lists")
        self.loadDictionary()

    def buildChannelList(self, phy):
        """
        Builds a list of channels for the given phy using iw list

        Args:
            phy (str): the physical interface to look for in iw list

        Returns:
            channels: a list of channels that can be used for scanning
        """
        channels = []
        output = subprocess.check_output(['iw', 'list'])
        text = output.decode("utf-8")
        list  = str(text).split("\n")

        for line in list:
            if '[' in line:
                channel = line.split("[")[1].split("]")[0]
                if channel.isnumeric():
                    channels.append(channel)

        #print(str(channels))
        return channels

    # enable monitor mode on the given interface
    def enableMonitorMode(self, interface):
        """Enables monitor mode on the given interface

        Args:
            interface (str): the interface to enable monitor mode on
        """

        print(f"Enabling monitor mode on {str(interface)}")
        
        os.system(f"ip link set {str(interface)} down")
        os.system(f"iw dev {str(interface)} set type monitor")
        os.system(f"ip link set {str(interface)} up")


    def callback(self, packet):
        """Callback method for scapy sniffing

        Args:
            packet (_type_): _description_
        """
        if packet.haslayer(Dot11Beacon):
            # extract the MAC address of the network
            bssid = packet[Dot11].addr2
            # get the name of it
            ssid = packet[Dot11Elt].info.decode()
            try:
                dbm_signal = packet.dBm_AntSignal
            except:
                dbm_signal = "N/A"
            # extract network stats
            stats = packet[Dot11Beacon].network_stats()
            # get the channel of the AP
            channel = stats.get("channel")
            # get the crypto
            crypto = stats.get("crypto")

            key = str(bssid).replace(':','').upper()[0:6]
            vendor = self.vendorDict.get(key)
            self.networks.loc[bssid] = (ssid, vendor, dbm_signal, channel, crypto)

    def print_all(self):
        while True:
            os.system("clear")
            print(self.networks)
            time.sleep(0.5)

    def change_channel(self):
        while True:
            for ch in self.channelList:
                print(f"Changing channel on {self.interface} to {ch}")
                os.system(f"iwconfig {self.interface} channel {ch}")
                time.sleep(0.5)

    def scanThread(self):
        """
        Thread for scapy sniff
        """
        sniff(iface=self.interface, prn=self.callback, stop_filter=lambda x: self.stopEvent.is_set())

        
    
    def startThreads(self, printing=False, channel_change=False, sniffing=True):
        """
        Starts all the threads

        Args:
            printing (bool, optional): True if starting the display thread. Defaults to False.
            channel_change (bool, optional): True if starting the channel changer thread. Defaults to False.
            sniffing (bool, optional): True if starting the scanner thread. Defaults to True.
        """
        # thread for printing the networks
        if printing:
            printThread = Thread(target=self.print_all, daemon=True)
            printThread.start()
        # thread for changing channel
        if channel_change:
            channelThread = Thread(target=self.change_channel, daemon=True)
            channelThread.start()
        # thread for sniffing
        if sniffing:
            sniffThread = Thread(target=self.scanThread, daemon=True)
            sniffThread.start()

    def downloadMACLists(self):
        """
        Downloads the three MAC block files from the web into the local directory
        """

        # The URL to the MA-L CSV - the Large Block Registry
        malURL = "http://standards-oui.ieee.org/oui/oui.csv"

        # this is the URL to the MA-M CSV - the Medium Block Registry
        mamURL = "http://standards-oui.ieee.org/oui28/mam.csv"

        # this is the URL to the MA-S CSV - the Small Bloc Registry
        masURL = "http://standards-oui.ieee.org/oui36/oui36.csv"

        print("Starting downloads:")

        # oui file
        print("Downloading oui.csv")
        data = requests.get(malURL)
        with open('oui.csv', 'wb') as file:
            file.write(data.content)

        print("Downloading mam.csv")
        # mam file
        data = requests.get(mamURL)
        with open('mam.csv', 'wb') as file:
            file.write(data.content)

        # oui36 file
        print("Downloading oui36.csv")
        data = requests.get(masURL)
        with open('oui36.csv', 'wb') as file:
            file.write(data.content)

    def loadDictionary(self):
        ''' Handles setting up the dictionary that will give the vendor identification'''

        with open('oui.csv', mode='r') as infile: # large registry
            reader = csv.reader(infile)

            self.vendorDict = {rows[1]:rows[2] for rows in reader}

            #print(f"{len(self.vendorDict)}")

        with open('mam.csv', mode='r') as infile: # medium registry
            reader = csv.reader(infile)

            midDict = {rows[1]:rows[2] for rows in reader}

            self.vendorDict.update(midDict)

            #print(f"{len(self.vendorDict)}")

        with open('oui36.csv', mode='r') as infile: # small registry
            reader = csv.reader(infile)

            smallDict = {rows[1]:rows[2] for rows in reader}

            self.vendorDict.update(smallDict)

            #print(f"{len(self.vendorDict)}")

    def stop(self):
        """
        Stops the threads
        """
        self.stopEvent.set()
        time.sleep(0.5)
        os.system(f"ip link set {str(interface)} down")
        os.system(f"ip link set {str(interface)} up")

if __name__ == "__main__":

    # Check to see if running as root
    if not os.geteuid() == 0 :
        print("Run as root.")
        exit(1)

    # interface name, check using iw
    interfaces = [] # list of interfaces
    phys = [] # list of physical interfaces
    output = os.popen("iw dev").read()
    list = output.split("\n")
    for line in list:
        if "phy" in line:
            phys.append(line)
        if "Interface" in line:
            interfaces.append(line.split(" ")[1])

    if len(interfaces) == 0:
        print("No interfaces found")
        exit(1)
    elif len(interfaces) == 1:
        interface = interfaces[0]
        phy = phys[0]
    else:
        for x in range(len(interfaces)):
            print(f"{x}: {interfaces[x]}")
        choice = input("Select interface: ")
        interface = interfaces[int(choice)]
        phy = phys[int(choice)]

    scanner = APScanner(interface, phy)
    scanner.startThreads(True, True, True)

    try:
        input("Press enter to stop...")
        scanner.stop()
        print("Stopped")
        print("Exiting...")
        exit(0)
    except KeyboardInterrupt:
        scanner.stop()
        print("Stopped")
        print("Exiting...")
        exit(0)