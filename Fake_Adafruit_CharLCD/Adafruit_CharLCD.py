import keyboard
import os

# Button Static Hardware Values
SELECT    = 0
RIGHT     = 1
DOWN      = 2
UP        = 3
LEFT      = 4


class Adafruit_CharLCDPlate():
    """Class to allow development without an actual LCD plate."""

    def set_color(self, r, g, b):
        print("COLOR: Color set to {}, {}, {}".format(r, g, b))

    def clear(self):
        os.system('clear')

    def message(self, message):
        message = message[:32] if len(message) > 32 else message
        if len(message) > 16 and '\n' not in message[0:16]:
            print(message[:16] + '\n' + message[16:32])
        else:
            print(message)

    def is_pressed(self, button):
        pressed = False
        if button is SELECT and keyboard.is_pressed('q'):
            pressed = True
        elif button is UP and keyboard.is_pressed('w'):
            pressed = True
        elif button is LEFT and keyboard.is_pressed('a'):
            pressed = True
        elif button is DOWN and keyboard.is_pressed('s'):
            pressed = True
        elif button is RIGHT and keyboard.is_pressed('d'):
            pressed = True
        return pressed
