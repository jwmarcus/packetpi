import re, time, platform
from pprint import pprint
import aprslib

# Run in "Fake" mode when not on the actual Raspberry Pi
if platform.node() in ['pulsar']:
    import Adafruit_CharLCD as LCD
else:
    import Fake_Adafruit_CharLCD as LCD

# Define some Menu indexes
MENU_POS = 0
MENU_CMT = 1
MENU_SPD = 2

MENU_OPTIONS = [{'text': "POS"},
                {'text': "CMT"},
                {'text': "SPD"}]

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

def get_lcd_message(packet, index, screen_type):
    lcd_message = str(index).zfill(2)
    lcd_message += "-" + MENU_OPTIONS[screen_type].get('text')
    lcd_message += ":" + packet.get('from')
    lcd_message += '\n'

    if screen_type is MENU_POS:
        lcd_message += format_lat_long(
            packet.get('latitude', 0.),
            packet.get('longitude', 0.)
        )
    elif screen_type is MENU_CMT:
        lcd_message += packet.get('comment', '')[0:16]
    elif screen_type is MENU_SPD:
        lcd_message += format_speed_course(
            packet.get('speed', 0.),
            packet.get('course', 0.)
        )

    return lcd_message

def format_lat_long(lat, long):
    pos_ns = "n" if lat >= 0 else "s"
    pos_we = "w" if long <= 0 else "e"
    deg_lat = "{:.0f}".format(abs(lat)).zfill(2)
    deg_long = "{:.0f}".format(abs(long)).zfill(3)
    dec_lat = "{:0.4f}".format(lat % 1)[2:]
    dec_long = "{:0.4f}".format(long % 1)[2:]
    combined_lat_long = deg_lat + pos_ns + dec_lat + ":"
    combined_lat_long += deg_long + pos_we + dec_long

    return combined_lat_long

def format_speed_course(speed, course):
    combined_speed_course = "SPD:"
    combined_speed_course += "{:.1f}".format(speed).zfill(4)
    combined_speed_course += "-CSE:"
    combined_speed_course += "{:.0f}".format(course).zfill(3)
    return combined_speed_course

def refresh_packets():
    ax_log = "./axlogs.txt"
    packets = [] # Packets ordered same as log file

    packet_strings = read_packets(ax_log)
    for packet in packet_strings:
        if (parse_packet(packet) is not None):
            packets.append(parse_packet(packet))
    return packets


def main():
    # every x seconds check for new packets and update packet table
    # every x seconds flip display between page1 and page2
    # contunuously check for a button press, debounce every 0.25sec

    packets = refresh_packets()

    for index, packet in enumerate(packets):
        for message_type in [MENU_SPD]: # MENU_POS, MENU_CMT,
            lcd.clear()
            lcd.message(get_lcd_message(packet, index, message_type))
            time.sleep(2)

if __name__ == "__main__":
    main()
