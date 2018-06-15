import os, time
from gps3 import gps3

class GPSMouse:
    'Base class for interacting with a USB GPS'

    gps_socket = None
    data_stream = None

    def __init__(self, port):
        # Kill everything that might be using gpsd
        os.system("killall gpsd")
        time.sleep(1)

        # Start gpsd
        os.system("gpsd {}".format(port))
        time.sleep(1)

        # The socket takes care of HW interaction, we read from the stream
        self.gps_socket = gps3.GPSDSocket()
        self.data_stream = gps3.DataStream()
        self.gps_socket.connect()
        self.gps_socket.watch()

    def read_position(self, options):
        # TODO: typecheck all the elements and replace "n/a"'s with something useful
        # TODO: Have this no block when there is no data
        data = None
        for new_data in self.gps_socket:
            if new_data:
                data = self.data_stream.unpack(new_data)
        return data

def main():
    gpsm = GPSMouse('/dev/ttyUSB0')
    pos = gpsm.read_position(None)
    print(pos)


if __name__ == "__main__":
    main()
