import re
import time
import Fake_Adafruit_CharLCD as LCD

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
    origin = search_except(origin_dest, r'[-A-Za-z0-9]+', 0)
    destination = search_except(origin_dest, r'[-A-Za-z0-9]+ to ([-A-Za-z0-9]+)', 1)
    message = search_except(packet, r'(.*?)(len [0-9 ]+)(.*)', 3)

    packet_dict = {
            'call_path': call_path,
            'message': message,
            'origin_dest': origin_dest,
            'origin': origin,
            'destination': destination
    }

    return packet_dict


def main():
    ax_log = "./axlogs.txt"
    packets = [] # Packets ordered same as log file

    packet_strings = read_packets(ax_log)
    for packet in packet_strings:
        packets.append(parse_packet(packet))

    # Make list of button value, text, and backlight color.
    buttons = ( (LCD.SELECT, 0 , (1,1,1)),
                (LCD.LEFT,   1 , (1,0,0)),
                (LCD.UP,     2 , (0,0,1)),
                (LCD.DOWN,   3 , (0,1,0)),
                (LCD.RIGHT,  4 , (1,0,1)) )

    lcd.set_color(1,0,0)
    lcd.clear()

    seed_time = int(round(time.time()))
    message_index = 0
    display_page = 0

    while True:
        # Switch between stations and message
        now_time = int(round(time.time()))
        if now_time % seed_time == 4:
            seed_time = int(round(time.time()))
            i = message_index
            lcd.clear()
            display_page = 1 - display_page # Sick way of flipping bits
            if display_page == 1:
                lcd.message("{0:03d}".format(i) + " " + packets[i].get("origin") + '\nto  ' + packets[i].get("destination"))
            else:
                lcd.message("{0:03d}".format(i) + " " + packets[i].get("message"))


        # Loop through each button and check if it is pressed.
        for button in buttons:
            if lcd.is_pressed(button[0]):
                message_index = button[1]
                display_page = 1
                seed_time = int(round(time.time()))
                lcd.clear()
                i = message_index
                lcd.message("{0:03d}".format(i) + " " + packets[i].get("origin") + '\nto  ' + packets[i].get("destination"))
                time.sleep(0.25)

if __name__ == "__main__":
    main()
