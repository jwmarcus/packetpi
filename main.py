import re, time, platform
from pprint import pprint
import aprslib

if platform.node() in ['pulsar']:
    import Adafruit_CharLCD as LCD
else:
    import Fake_Adafruit_CharLCD as LCD

# Initialize the LCD using the pins
lcd = LCD.Adafruit_CharLCDPlate()

def read_packets(logfile):
    packets = []

    with open(logfile, 'r') as f:
        payload = f.read().replace('\n','')
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
    parsed_packet = None
    f_packet = format_packet(packet)

    try:
        parsed_packet = aprslib.parse(f_packet)
    except (aprslib.exceptions.UnknownFormat):
        print('INFO: Undecodable Message: {}'.format(f_packet))
    return parsed_packet

def format_packet(packet):
    call_path = search_except(packet, r'^.+(?= ctl UI)', 0)
    call_path = re.sub(r' to ', r'>', call_path)
    call_path = re.sub(r' via ', r',', call_path)
    call_path = re.sub(r' ', r',', call_path)

    message = search_except(packet, r'(.*?)(len [0-9 ]+)(.*)', 3)
    message = re.sub(r'0[0-9]+  ', r'', message) # remove packet new lines

    return call_path + ':' + message

def get_lcd_message(packet_dict, index):
    lcd_message = packet_dict.get('from')
    lcd_message += ">"
    lcd_message += packet_dict.get('to')
    lcd_message += '\n'
    lcd_message += packet_dict.get('comment', '')
    return lcd_message

def refresh_packets():
    ax_log = "./axlogs.txt"
    packets = [] # Packets ordered same as log file

    packet_strings = read_packets(ax_log)
    for packet in packet_strings:
        if (parse_packet(packet) is not None):
            packets.append(parse_packet(packet))
    return packets


def main():
    time_now = int(round(time.time()))

    # every x seconds check for new packets and update packet table
    # every x seconds flip display between page1 and page2
    # contunuously check for a button press, debounce every 0.25sec

    # Demo reel for all packets parsed
    packets = refresh_packets()

    for index, packet in enumerate(packets):
        lcd.clear()
        lcd.message(get_lcd_message(packet, index))
        time.sleep(3)

if __name__ == "__main__":
    main()
