from scapy.all import Dot11, Dot11Beacon, Dot11Elt, RadioTap, sendp, hexdump, sniff # needed for generating packet
import os # needed for OS commands

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

ap_list = []

def PacketHandler(packet):
    if packet.haslayer(Dot11):
        if packet.type == 0 and packet.subtype == 8:
            if packet.addr2 not in ap_list:
                ap_list.append(packet.addr2)
                print("Access Point MAC: %s with SSID: %s " %(packet.addr2, packet.info))

enableMonitorMode("wlx9cefd5fd14f7")
sniff(iface="wlx9cefd5fd14f7", prn = PacketHandler)
#enableMonitorMode("wlx00c0cab08f8d")
#sniff(iface="wlx00c0cab08f8d", prn = PacketHandler)
