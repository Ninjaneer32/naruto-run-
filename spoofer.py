


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