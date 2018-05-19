import re
import time
import Adafruit_CharLCD as LCD

# Initialize the LCD using the pins
lcd = LCD.Adafruit_CharLCDPlate()

def read_packets(logfile):
    packets = []

    with open(logfile, 'r') as f:
        payload = f.read().replace('\n', '')
        packets = payload.split('1: fm ')
        if len(packets) > 0:
            packets.pop(0) # First element is always blank

    return packets


def search_except(payload, pattern, group_index):
    m = re.search(pattern, payload)
    if m == None: # No callsign path was found
        raise Exception("Error: Pattern Not Found " + pattern)
    return m.group(group_index)


def parse_packet(packet):
    # get entire path, then extract origin and call, then extract path:
    call_path = search_except(packet, r'.*(?= ctl UI)', 0)
    origin_dest = search_except(call_path, r'[-A-Za-z0-9]+ to [-A-Za-z0-9]+', 0)
    call_path = call_path.replace(origin_dest, "").lstrip()
    message = search_except(packet, r'(.*?)(len [0-9 ]+)(.*)', 3)

    packet_dict = {
            'call_path': call_path,
            'message': message,
            'origin_dest': origin_dest
    }

    return packet_dict


def main():
    ax_log = "./axlogs.txt"
    packets = [] # Packets ordered same as log file

    packet_strings = read_packets(ax_log)
    for packet in packet_strings:
        packets.append(parse_packet(packet))

    while True:
        lcd.set_color(1.0, 0.0, 0.0)
        lcd.clear()
        lcd.message(packets[3].origin_dest + '\n' + packets[3].origin_dest)
        time.sleep(3.0)
        lcd.set_color(0.0, 1.0, 0.0)
        lcd.clear()
        lcd.message('Line 3\nLine4')
        time.sleep(3.0)


if __name__ == "__main__":
    main()
