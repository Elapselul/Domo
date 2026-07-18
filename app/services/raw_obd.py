import glob
import re
import threading
import time

import serial


class RawOBDError(Exception):
    """Raised when an OBD request fails."""


class RawOBD:
    def __init__(self, port: str | None = None, baud: int = 115200):
        self.port = port
        self.baud = baud
        self.serial: serial.Serial | None = None
        self.lock = threading.Lock()

    def _find_ports(self) -> list[str]:
        if self.port:
            return [self.port]

        return sorted(
            glob.glob("/dev/ttyUSB*")
            + glob.glob("/dev/ttyACM*")
        )

    def connect(self) -> None:
        last_error: Exception | None = None

        # Give Linux time to finish detecting the USB adapter.
        time.sleep(3)

        for attempt in range(1, 11):
            ports = self._find_ports()

            if not ports:
                print(
                    f"DOMO: Waiting for USB adapter "
                    f"({attempt}/10)..."
                )
                time.sleep(2)
                continue

            for port in ports:
                try:
                    print(
                        f"DOMO: Trying {port} "
                        f"(attempt {attempt}/10)"
                    )

                    # Completely close any previous serial connection.
                    self.close()
                    time.sleep(0.5)

                    self.serial = serial.Serial(
                        port=port,
                        baudrate=self.baud,
                        timeout=3,
                        write_timeout=2,
                    )

                    self.port = port

                    # Toggle the serial control lines to help reset
                    # an adapter that was opened during startup.
                    self.serial.dtr = False
                    self.serial.rts = False
                    time.sleep(0.5)

                    self.serial.dtr = True
                    self.serial.rts = True
                    time.sleep(1.0)

                    # Clear anything left in the serial buffers.
                    self.serial.reset_input_buffer()
                    self.serial.reset_output_buffer()

                    setup_commands = [
                        ("ATZ", 1.5),
                        ("ATE0", 0.2),
                        ("ATL1", 0.2),
                        ("ATS1", 0.2),
                        ("ATH1", 0.2),
                        ("ATSP6", 0.5),
                        ("ATCAF1", 0.2),
                    ]

                    for command, delay in setup_commands:
                        response = self.send_raw(
                            command,
                            delay=delay,
                        )

                        if (
                            "?" in response
                            or "UNABLE TO CONNECT" in response
                            or "BUS ERROR" in response
                        ):
                            raise RawOBDError(
                                f"{command} failed: {response.strip()}"
                            )

                    # Do not call it connected until the ECU answers.
                    print("DOMO: Checking ECU response...")

                    rpm_payload = self.pid(0x0C)

                    if (
                        len(rpm_payload) < 4
                        or rpm_payload[0:2] != bytes((0x41, 0x0C))
                    ):
                        raise RawOBDError(
                            "ECU did not return a valid RPM response"
                        )

                    print(f"DOMO: Connected on {port}")
                    return

                except (
                    serial.SerialException,
                    RawOBDError,
                    OSError,
                ) as error:
                    last_error = error
                    print(f"DOMO: Attempt failed: {error}")
                    self.close()
                    time.sleep(2)

        raise RawOBDError(
            "Could not connect after 10 attempts. "
            f"Last error: {last_error}"
        )
        
    def close(self) -> None:
        if self.serial is not None:
            try:
                if self.serial.is_open:
                    self.serial.close()
            finally:
                self.serial = None

    def send_raw(self, command: str, delay: float = 0.08) -> str:
        if self.serial is None or not self.serial.is_open:
            raise RawOBDError("OBD adapter is not connected")

        with self.lock:
            try:
                self.serial.reset_input_buffer()
                self.serial.write((command + "\r").encode("ascii"))
                self.serial.flush()

                time.sleep(delay)

                response = self.serial.read_until(b">")

                if not response:
                    raise RawOBDError(
                        f"No response to command {command}"
                    )

                return response.decode(
                    "ascii",
                    errors="replace",
                )

            except serial.SerialException as error:
                self.close()
                raise RawOBDError(
                    f"Serial connection failed: {error}"
                ) from error

    @staticmethod
    def _extract_can_frames(response: str) -> list[list[int]]:
        frames: list[list[int]] = []

        for line in response.replace("\r", "\n").splitlines():
            line = line.strip().upper()

            if not line:
                continue

            if any(message in line for message in (
                "OK",
                "NO DATA",
                "STOPPED",
                "SEARCHING",
                "UNABLE TO CONNECT",
                "BUS ERROR",
            )):
                continue

            # Expected format:
            # 7E8 04 41 0C 0A EF
            tokens = re.findall(r"\b[0-9A-F]{2,3}\b", line)

            if len(tokens) < 2:
                continue

            # First token is the 11-bit CAN header, e.g. 7E8.
            if len(tokens[0]) != 3:
                continue

            try:
                data = [int(token, 16) for token in tokens[1:]]
            except ValueError:
                continue

            if data:
                frames.append(data)

        return frames

    @staticmethod
    def _reassemble_isotp(frames: list[list[int]]) -> bytes:
        if not frames:
            raise RawOBDError("No CAN frames found in response")

        first = frames[0]
        frame_type = first[0] >> 4

        # ISO-TP single frame:
        # 04 41 0C 0A EF
        if frame_type == 0x0:
            payload_length = first[0] & 0x0F
            payload = first[1:1 + payload_length]

            if len(payload) < payload_length:
                raise RawOBDError("Incomplete single-frame response")

            return bytes(payload)

        # ISO-TP first frame:
        # 10 0C 41 70 ...
        if frame_type == 0x1:
            if len(first) < 2:
                raise RawOBDError("Invalid ISO-TP first frame")

            total_length = (
                ((first[0] & 0x0F) << 8)
                | first[1]
            )

            payload = list(first[2:])
            expected_sequence = 1

            for frame in frames[1:]:
                if not frame:
                    continue

                current_type = frame[0] >> 4

                if current_type != 0x2:
                    continue

                sequence = frame[0] & 0x0F

                if sequence != expected_sequence:
                    raise RawOBDError(
                        "Unexpected ISO-TP sequence number: "
                        f"expected {expected_sequence:X}, "
                        f"received {sequence:X}"
                    )

                payload.extend(frame[1:])
                expected_sequence = (
                    expected_sequence + 1
                ) & 0x0F

                if len(payload) >= total_length:
                    break

            if len(payload) < total_length:
                raise RawOBDError(
                    f"Incomplete ISO-TP response: "
                    f"expected {total_length} payload bytes, "
                    f"received {len(payload)}"
                )

            return bytes(payload[:total_length])

        raise RawOBDError(
            f"Unsupported ISO-TP frame type: 0x{frame_type:X}"
        )

    def pid(self, pid: int) -> bytes:
        response = self.send_raw(f"01{pid:02X}")
        frames = self._extract_can_frames(response)
        payload = self._reassemble_isotp(frames)

        if len(payload) < 2:
            raise RawOBDError(
                f"PID 0x{pid:02X} returned a short response"
            )

        if payload[0] == 0x7F:
            service = payload[1] if len(payload) > 1 else 0
            code = payload[2] if len(payload) > 2 else 0

            raise RawOBDError(
                f"ECU rejected service 0x{service:02X}, "
                f"code 0x{code:02X}"
            )

        expected_service = 0x41

        if payload[0] != expected_service or payload[1] != pid:
            raise RawOBDError(
                f"Unexpected response for PID 0x{pid:02X}: "
                f"{payload.hex(' ').upper()}"
            )

        return payload