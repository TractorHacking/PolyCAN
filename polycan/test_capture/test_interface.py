import time
import unittest
import capture.interfaces as interfaces
import can


class MyTestCase(unittest.TestCase):
    def test_slcan_config(self):
        bus = interfaces.can_int(interfaces.slcan_config())
        try:
            while True:
                msg = bus.recv(1)
                if msg is not None:
                    print(bin(msg))
        except KeyboardInterrupt:
            bus.shutdown()
            pass


if __name__ == '__main__':
    unittest.main()
