import serial
import threading
import time


class RawOBD:

    def __init__(self, port="/dev/ttyUSB0", baud=115200):
        self.port = port
        self.baud = baud
        self.serial = None
        self.lock = threading.Lock()

    def connect(self):

        self.serial = serial.Serial(
            self.port,
            self.baud,
            timeout=2,
        )

        setup = [
            "ATZ",
            "ATE0",
            "ATL0",
            "ATS0",
            "ATH1",
            "ATSP6",
        ]

        for cmd in setup:
            self.send(cmd)

    def send(self, command):

        with self.lock:

            self.serial.reset_input_buffer()

            self.serial.write((command + "\r").encode())

            self.serial.flush()

            time.sleep(0.08)

            response = self.serial.read_until(b">")

            return (
                response
                .decode(errors="ignore")
                .replace("\r", "")
                .replace("\n", "")
                .replace(">", "")
                .strip()
            )

    def pid(self, pid):

        return self.send(f"01{pid:02X}")