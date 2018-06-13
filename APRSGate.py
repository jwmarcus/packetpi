import re, os, time
import aprslib

class APRSGate:
    'Base class for creating an APRS Gateway'

    log_file = "./axlogs.txt"

    def __init__(self, hardware_tnc):
        if hardware_tnc:
            self.setup_aprs_listener()

    def setup_aprs_listener(self):
        # Kill everything that might be using AX Tools
        os.system("sudo killall kissattach")
        os.system("sudo killall axlisten")

        # Attach the device to AXPORTS device "1"
        os.system("sudo kissattach /dev/ttyAMA0 1")
        time.sleep(1)

        # Start a log of axlisten
        os.system("sudo axlisten -a > aprslogs.txt &")
        self.log_file = "./aprslogs.txt"

    def get_packets(self):
        packets = [] # Packets ordered same as log file

        packet_strings = self.read_packet_log(self.log_file)
        for packet in packet_strings:
            if (self.parse_packet(packet) is not None):
                packets.append(self.parse_packet(packet))
        return packets

    def read_packet_log(self, logfile):
        packets = []

        with open(logfile, 'r') as f:
            payload = f.read().replace('\n','')
            packets = payload.split('1: fm ')
            if len(packets) > 0:
                packets.pop(0) # First element is always blank
        return packets

    def parse_packet(self, packet):
        parsed_packet = None
        f_packet = self.reformat_packet(packet)

        try:
            parsed_packet = aprslib.parse(f_packet)
        except (aprslib.exceptions.UnknownFormat):
            # print('INFO: Undecodable Message: {}'.format(f_packet))
            pass
        return parsed_packet

    def reformat_packet(self, packet):
        call_path = self.search_except(packet, r'^.+(?= ctl UI)', 0)
        call_path = re.sub(r' to ', r'>', call_path)
        call_path = re.sub(r' via ', r',', call_path)
        call_path = re.sub(r' ', r',', call_path)

        message = self.search_except(packet, r'(.*?)(len [0-9 ]+)(.*)', 3)
        message = re.sub(r'0[0-9]+  ', r'', message) # remove packet new lines

        return call_path + ':' + message

    def search_except(self, payload, pattern, group_index):
        m = re.search(pattern, payload)
        if m == None: # No callsign path was found
            raise Exception("Error: Pattern Not Found " + pattern)
        return m.group(group_index)
