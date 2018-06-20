import os, time
from gps3.agps3threaded import AGPS3mechanism

class GPSMouse:
    'Base class for interacting with a USB GPS'

    agps_thread = None

    def __init__(self, port='/dev/ttyUSB0'):
        # Kill everything that might be using gpsd
        os.system("killall gpsd")
        time.sleep(1)
        os.system("gpsd {}".format(port))
        time.sleep(1)

        # The socket takes care of HW interaction, we read from the stream
        self.agps_thread = AGPS3mechanism()
        self.agps_thread.stream_data()
        self.agps_thread.run_thread()

    def read_position(self):
        # TODO: typecheck all the elements and replace "n/a"'s with something useful
        return dir(self.agps_thread.data_stream)

# def main():
#     gpsm = GPSMouse('/dev/ttyUSB0')
#     while True:
#         pos = gpsm.read_position()
#         print(pos)
#         time.sleep(0.2)
#
# if __name__ == "__main__":
#     main()
