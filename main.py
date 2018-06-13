import time, platform
from APRSGate import APRSGate
from PacketMenu import PacketMenu

# Does this machine have physical hardware?
hw_nodes = ['pulsar']
is_hardware = True if platform.node() in hw_nodes else False

# Import the appropriate LCD package
if is_hardware:
    import Adafruit_CharLCD as LCD
else:
    import Fake_Adafruit_CharLCD as LCD

def main():
    # Initialize the APRSGate, passing in current machine name
    agate = APRSGate(is_hardware)
    packets = agate.get_packets()

    # Initialize the LCD
    lcd = LCD.Adafruit_CharLCDPlate()
    lcd.set_color(1, 0, 0)

    # Create a menu
    menu = PacketMenu()

    while True:
        # Poll the switches on LCD board
        button_num = menu.get_button(lcd)
        if button_num is not None:
            menu.update_indexes(button_num, len(packets))
            menu.update_lcd(packets, lcd)

        # Refresh the display every refresh_rate seconds
        if menu.time_for_update(4):
            menu.update_time()
            last_pack_len = len(packets)
            packets = agate.get_packets()
            if len(packets) > last_pack_len:
                menu.blink_alert(lcd, ((1,0,0)), ((0,1,0)), 10, 0.25)


if __name__ == "__main__":
    main()
