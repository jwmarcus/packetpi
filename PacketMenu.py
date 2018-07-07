import time, re

class PacketMenu:
    # Define some Menu indexes
    MENU_POS  = 0
    MENU_CMT  = 1
    MENU_SPD  = 2
    MENU_PATH = 3

    # Button Static Hardware Values
    LCD_SELECT    = 0
    LCD_RIGHT     = 1
    LCD_DOWN      = 2
    LCD_UP        = 3
    LCD_LEFT      = 4

    MENU_TYPE_VIEWER = 0
    MENU_TYPE_INFO   = 1

    SCREEN_TYPES = [MENU_POS, MENU_CMT, MENU_SPD, MENU_PATH]
    MENU_TYPES = [MENU_TYPE_VIEWER, MENU_TYPE_INFO]
    LCD_BUTTONS = [LCD_SELECT, LCD_RIGHT, LCD_DOWN, LCD_UP, LCD_LEFT]

    MENU_OPTIONS = [{'text': "POS"},
                    {'text': "CMT"},
                    {'text': "SPD"},
                    {'text': "PTH"}]


    # Menu system
    packet_index = 0 # Index of which message to display
    page_index = MENU_POS   # Index of which page of data to dispay
    menu_index = MENU_TYPE_VIEWER
    refresh_rate = 6
    start_time = None
    gps_position = None

    def __init__(self):
        self.update_time()

    def update_time(self):
        self.start_time = int(round(time.time()))

    def time_for_update(self, refresh_rate):
        return (int(round(time.time())) % self.start_time) >= refresh_rate

    def update_lcd(self, packets, lcd):
        formatted_message = self.get_lcd_message(
                packets[self.packet_index] if len(packets) is not 0 else None,
                self.packet_index,
                self.page_index,
                self.menu_index)
        lcd.clear()
        lcd.message(formatted_message)
        time.sleep(0.15) # slight de-bounce

    def get_lcd_message(self, packet, packet_index, page_index, menu_type):
        lcd_message = ""

        if menu_type is self.MENU_TYPE_VIEWER and packet is not None:
            lcd_message += str(packet_index).zfill(2)
            lcd_message += "-" + self.MENU_OPTIONS[page_index].get('text')
            lcd_message += ":" + packet.get('from')
            lcd_message += '\n'

            if page_index is self.MENU_POS:
                lcd_message += self.format_lat_long(
                    packet.get('latitude', 0.),
                    packet.get('longitude', 0.)
                )
            elif page_index is self.MENU_CMT:
                lcd_message += packet.get('comment', '')[0:16]
            elif page_index is self.MENU_SPD:
                lcd_message += self.format_speed_course(
                    packet.get('speed', 0.),
                    packet.get('course', 0.)
                )
            elif page_index is self.MENU_PATH:
                lcd_message += self.format_path(packet.get('path', ''))
        elif menu_type is self.MENU_TYPE_INFO:
            lcd_message += "Press UP to\nReset Messages"
        return lcd_message

    def format_lat_long(self, lat, long):
        pos_ns = "n" if lat >= 0 else "s"
        pos_we = "w" if long <= 0 else "e"
        deg_lat = "{:.0f}".format(abs(int(lat))).zfill(2)
        deg_long = "{:.0f}".format(abs(int(long))).zfill(3)
        dec_lat = "{:0.4f}".format(abs(lat))[3:]
        dec_long = "{:0.4f}".format(abs(long))[3:]
        combined_lat_long = deg_lat + pos_ns + dec_lat + ":"
        combined_lat_long += deg_long + pos_we + dec_long

        return combined_lat_long

    def format_speed_course(self, speed, course):
        combined_speed_course = "SPD:"
        combined_speed_course += "{:.0f}".format(speed).zfill(3)
        combined_speed_course += "--CSE:"
        combined_speed_course += "{:.0f}".format(course).zfill(3)
        return combined_speed_course

    def format_path(self, path):
        path_str = ""
        for path_node in path:
            path_str += re.sub(r'WIDE', r'W', path_node)
        return path_str[0:16]

    def update_indexes(self, button_num, packets):
        if button_num is self.LCD_UP and self.menu_index is self.MENU_TYPE_INFO:
            # TODO: Reset the cache, blow away past packets
            pass

        if button_num is self.LCD_SELECT:
            self.menu_index = (self.menu_index + 1) % len(self.MENU_TYPES)

        if len(packets) is 0: # Empty list of packets, can't update indexes
            return

        if button_num is self.LCD_UP:
            self.packet_index = (self.packet_index + 1) % len(packets)
        elif button_num is self.LCD_DOWN:
            self.packet_index = (self.packet_index - 1) % len(packets)
        elif button_num is self.LCD_RIGHT:
            self.page_index = (self.page_index + 1) % len(self.SCREEN_TYPES)
        elif button_num is self.LCD_LEFT:
            self.page_index = (self.page_index - 1) % len(self.SCREEN_TYPES)

    def update_position(self, gps_position):
        self.gps_position = gps_position

    def get_position(self):
        current_position = self.gps_position
        # TODO: Do some parsing and error checking for bad location values
        return self.gps_position

    def get_button(self, lcd):
        button_num = None
        for button in self.LCD_BUTTONS:
            if lcd.is_pressed(button):
                button_num = button
        return button_num

    def blink_alert(self, lcd, color1, color2, iterations, speed):
        for _ in range(iterations):
            lcd.set_color(*color2)
            time.sleep(speed)
            lcd.set_color(*color1)
            time.sleep(speed)
