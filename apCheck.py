from scapy.all import Dot11, Dot11Beacon, Dot11Elt, RadioTap, sendp, hexdump, sniff # needed for generating packet
import os # needed for OS commands
import pandas # needed for display
import time # needed for sleep
from threading import Thread # needed for multithreading

class APScanner:
    ''' Class that handles the scanning of the APs '''

    def __init__(self, interface):
        ''' init method '''

        self.interface = interface
        self.enableMonitorMode(self.interface)
        # initialize the networks dataframe that will contain all access points nearby
        self.networks = pandas.DataFrame(columns=["BSSID", "SSID", "dBm_Signal", "Channel", "Crypto"])
        # set the index BSSID (MAC address of the AP)
        self.networks.set_index("BSSID", inplace=True)

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
        ch = 1
        while True:
            print(f"Changing channel on {self.interface} to {ch}")
            os.system(f"iwconfig {self.interface} channel {ch}")
            # switch channel from 1 to 14 each 0.5s
            ch = ch % 14 + 1
            time.sleep(0.5)
    
    def startThreads(self):
        """
        Starts all the threads
        """
        # thread for printing the networks
        t1 = Thread(target=self.print_all, daemon=True)
        t1.start()
        # thread for changing channel
        t2 = Thread(target=self.change_channel, daemon=True)
        t2.start()
        sniff(iface=self.interface, prn=self.callback)


if __name__ == "__main__":

    # interface name, check using iw
    interfaces = [] # list of interfaces
    output = os.popen("iw dev").read()
    list = output.split("\n")
    for line in list:
        if "Interface" in line:
            interfaces.append(line.split(" ")[1])

    if len(interfaces) == 0:
        print("No interfaces found")
        exit(1)
    elif len(interfaces) == 1:
        interface = interfaces[0]
    else:
        for x in range(len(interfaces)):
            print(f"{x}: {interfaces[x]}")
        interface = interfaces[int(input("Select the interface: "))]

    scanner = APScanner(interface)
    scanner.startThreads()
