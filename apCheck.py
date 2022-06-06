from scapy.all import Dot11, Dot11Beacon, Dot11Elt, RadioTap, sendp, hexdump, sniff # needed for generating packet
import os # needed for OS commands
import pandas # needed for display
import time # needed for sleep
from threading import Thread # needed for multithreading

# used to scan for all wireless interfaces
def scanInterface():
    interfaces = [] # list of interfaces
    output = os.popen("iw dev").read()
    list = output.split("\n")
    for line in list:
        if "Interface" in line:
            interfaces.append(line.split(" ")[1])
    return interfaces

# enable monitor mode on the given interface
def enableMonitorMode(interface):
    print(f"Enabling monitor mode on {str(interface)}")
    
    os.system(f"ip link set {str(interface)} down")
    os.system(f"iw dev {str(interface)} set type monitor")
    os.system(f"ip link set {str(interface)} up")

# initialize the networks dataframe that will contain all access points nearby
networks = pandas.DataFrame(columns=["BSSID", "SSID", "dBm_Signal", "Channel", "Crypto"])
# set the index BSSID (MAC address of the AP)
networks.set_index("BSSID", inplace=True)

def callback(packet):
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
        networks.loc[bssid] = (ssid, dbm_signal, channel, crypto)

def print_all():
    while True:
        os.system("clear")
        print(networks)
        time.sleep(0.5)

def change_channel():
    ch = 1
    while True:
        os.system(f"iwconfig {interface} channel {ch}")
        # switch channel from 1 to 14 each 0.5s
        ch = ch % 14 + 1
        time.sleep(0.5)




if __name__ == "__main__":
    # interface name, check using iwconfig
    interface = "wlx9cefd5fcd2ba"
    # start the thread that prints all the networks
    printer = Thread(target=print_all)
    printer.daemon = True
    printer.start()
    channel_changer = Thread(target=change_channel)
    channel_changer.daemon = True
    channel_changer.start()
    # start sniffing
    sniff(prn=callback, iface=interface)

#enableMonitorMode("wlx9cefd5fcd2ba")
#sniff(iface="wlx9cefd5fcd2ba", prn = PacketHandler)
#enableMonitorMode("wlx9cefd5fd14f7")
#sniff(iface="wlx9cefd5fd14f7", prn = PacketHandler)
#enableMonitorMode("wlx00c0cab08f8d")
#sniff(iface="wlx00c0cab08f8d", prn = PacketHandler)
