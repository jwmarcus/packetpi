import os, time
from gps3.agps3threaded import AGPS3mechanism

class GPSMouse:
    'Base class for interacting with a USB GPS'

    agps_thread = None
    is_hardware_platform = False

    def __init__(self, port='/dev/ttyUSB0', is_hardware_platform=False):
        # TODO: Let this inherit from the actual hardware
        if is_hardware_platform:
            self.is_hardware_platform
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
        location = None
        if (self.is_hardware_platform):
            location = dir(self.agps_thread.data_stream)
        return location
