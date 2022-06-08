from scapy.all import Dot11, Dot11Beacon, Dot11Elt, RadioTap, sendp, hexdump, sniff # needed for generating packet
import os # needed for OS commands
import pandas # needed for display
import time # needed for sleep
from threading import Thread, Event # needed for multithreading
import subprocess # needed for OS commands

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
        self.networks = pandas.DataFrame(columns=["BSSID", "SSID", "dBm_Signal", "Channel", "Crypto"])
        # set the index BSSID (MAC address of the AP)
        self.networks.set_index("BSSID", inplace=True)

        self.stopEvent = Event()

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

        print(str(channels))
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
            self.networks.loc[bssid] = (ssid, dbm_signal, channel, crypto)

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
    #scanner.startThreads(True, True, True)

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