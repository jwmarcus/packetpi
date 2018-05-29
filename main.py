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

SCREEN_TYPES = [MENU_POS, MENU_CMT, MENU_SPD]

MENU_OPTIONS = [{'text': "POS"},
                {'text': "CMT"},
                {'text': "SPD"}]

LCD_BUTTONS = ((LCD.SELECT, 0, (1,1,1)),
               (LCD.LEFT,   1, (1,0,0)),
               (LCD.UP,     2, (0,0,1)),
               (LCD.DOWN,   3, (0,1,0)),
               (LCD.RIGHT,  4, (1,0,1)))


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
        # print('INFO: Undecodable Message: {}'.format(f_packet))
        pass
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

def update_lcd(packet, index, screen_type, lcd):


    formatted_message = get_lcd_message(packet, index, screen_type)
    lcd.clear()
    lcd.message(formatted_message)
    time.sleep(0.15) # slight de-bounce?

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
    combined_speed_course += "{:.0f}".format(speed).zfill(3)
    combined_speed_course += "--CSE:"
    combined_speed_course += "{:.0f}".format(course).zfill(3)
    return combined_speed_course

def refresh_packets():
    ax_log = "./blanklog.txt"
    packets = [] # Packets ordered same as log file

    packet_strings = read_packets(ax_log)
    for packet in packet_strings:
        if (parse_packet(packet) is not None):
            packets.append(parse_packet(packet))
    return packets

def get_button(lcd):
    button_num = None
    for button in LCD_BUTTONS:
        if lcd.is_pressed(button[0]):
            button_num = button[0]
    return button_num

def update_indexes(button_num, packet_index, page_index, packet_len, page_len):
    if packet_len is 0 or page_len is 0: # Bail out with empty lists
        return (packet_index, page_index)

    if button_num is LCD.UP:
        packet_index = (packet_index + 1) % packet_len
    elif button_num is LCD.DOWN:
        packet_index = (packet_index - 1) % packet_len
    elif button_num is LCD.RIGHT:
        page_index = (page_index + 1) % page_len
    elif button_num is LCD.LEFT:
        page_index = (page_index - 1) % page_len

    return (packet_index, page_index)

def blink_alert(lcd, color1, color2, iterations, speed):
    for _ in range(iterations):
        lcd.set_color(*color2)
        time.sleep(speed)
        lcd.set_color(*color1)
        time.sleep(speed)

def main():
    # Initialize the LCD using the pins
    lcd = LCD.Adafruit_CharLCDPlate()
    lcd.set_color(1, 0, 0)
    # Get first packets
    packets = refresh_packets()

    # TODO: Setup and tear down message queue from python

    # Menu system
    packet_index = 0 # Index of which message to display
    page_index = 0   # Index of which page of data to dispay
    refresh_rate = 6
    start_time = int(round(time.time()))

    # Put first message on screen
    if len(packets) > 0:
        update_lcd(packets[packet_index], packet_index, SCREEN_TYPES[page_index], lcd)

    while True:
        # Constantly check for button events
        button_num = get_button(lcd)
        if button_num is not None:
            packet_index, page_index = update_indexes(
                    button_num,
                    packet_index,
                    page_index,
                    len(packets),
                    len(SCREEN_TYPES)
            )
            if len(packets) > 0:
                update_lcd(packets[packet_index], packet_index, SCREEN_TYPES[page_index], lcd)

        # Refresh the display every refresh_rate seconds
        current_time = int(round(time.time()))
        if current_time % start_time == 4:
            start_time = current_time
            last_pack_len = len(packets)
            packets = refresh_packets()
            if len(packets) > last_pack_len:
                last_pack_len = len(packets)
                blink_alert(lcd, ((1,0,0)), ((0,1,0)), 2, 0.25)


if __name__ == "__main__":
    main()
