import os, time
from gps3 import gps3

class GPSMouse:
    'Base class for interacting with a USB GPS'

    gps_socket = None
    data_stream = None

    def __init__(self):
        # The socket takes care of HW interaction, we read from the stream
        this.gps_socket = gps3.GPSDSocket()
        this.data_stream = gps3.DataStream()
        this.gps_socket.connect()
        this.gps_socket.watch()

    def read_position(self, options):
        # TODO: typecheck all the elements and replace "n/a"'s with something useful
        data = None
        for new_data in this.gps_socket:
            print(new_data)
            if new_data:
                data = this.data_stream.unpack(new_data)
        return data
