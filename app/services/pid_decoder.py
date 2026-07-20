from dataclasses import dataclass


KPA_TO_PSI = 0.1450377377


class PIDDecodeError(ValueError):
    """Raised when an OBD PID payload is invalid."""


@dataclass(frozen=True)
class BoostData:
    commanded_kpa_absolute: float
    actual_kpa_absolute: float
    commanded_psi_absolute: float
    actual_psi_absolute: float
    commanded_psi_gauge: float
    actual_psi_gauge: float
    control_status: int


def decode_rpm(payload: bytes) -> float:
    """
    Decode Mode 01 PID 0x0C.

    Expected payload:
        41 0C A B
    """
    if len(payload) < 4 or payload[0:2] != bytes((0x41, 0x0C)):
        raise PIDDecodeError(
            f"Invalid RPM payload: {payload.hex(' ').upper()}"
        )

    raw = (payload[2] << 8) | payload[3]
    return raw / 4.0


def decode_boost(
    payload: bytes,
    atmospheric_kpa: float = 101.325,
) -> BoostData:
    """
    Decode Mode 01 PID 0x70 boost pressure control.

    Expected payload:
        41 70 A B C D E F G H I J

    B/C = commanded boost pressure A
    D/E = boost pressure sensor A

    Pressure values are absolute pressure:
        kPa = raw / 32
    """
    if len(payload) < 12 or payload[0:2] != bytes((0x41, 0x70)):
        raise PIDDecodeError(
            f"Invalid PID 0x70 payload: {payload.hex(' ').upper()}"
        )

    commanded_raw = (payload[3] << 8) | payload[4]
    actual_raw = (payload[5] << 8) | payload[6]

    commanded_kpa_absolute = commanded_raw / 32.0
    actual_kpa_absolute = actual_raw / 32.0

    commanded_kpa_gauge = (
        commanded_kpa_absolute - atmospheric_kpa
    )
    actual_kpa_gauge = actual_kpa_absolute - atmospheric_kpa

    return BoostData(
        commanded_kpa_absolute=commanded_kpa_absolute,
        actual_kpa_absolute=actual_kpa_absolute,
        commanded_psi_absolute=(
            commanded_kpa_absolute * KPA_TO_PSI
        ),
        actual_psi_absolute=(
            actual_kpa_absolute * KPA_TO_PSI
        ),
        commanded_psi_gauge=(
            commanded_kpa_gauge * KPA_TO_PSI
        ),
        actual_psi_gauge=(
            actual_kpa_gauge * KPA_TO_PSI
        ),
        control_status=payload[11],
    )

def decode_coolant(payload: bytes | list[int]) -> float:
    """
    Mode 01 PID 05.

    Formula:
        coolant °C = A - 40
    """
    data = list(payload)

    if len(data) < 1:
        raise ValueError("Coolant payload is empty")

    return float(data[0] - 40)


def decode_egt(payload: bytes | list[int]) -> float:
    """
    Mode 01 PID 78 — exhaust gas temperature, bank 1.

    The first byte indicates available EGT sensors.
    Each available sensor temperature uses two bytes:

        temperature °C = raw / 10 - 40

    DOMO returns the first valid sensor value.
    """
    data = list(payload)

    if len(data) < 3:
        raise ValueError(
            f"EGT payload is too short: {data}"
        )

    # Byte zero is the sensor-support bitmap.
    sensor_data = data[1:]

    for index in range(0, len(sensor_data) - 1, 2):
        high_byte = sensor_data[index]
        low_byte = sensor_data[index + 1]

        raw_value = (high_byte << 8) | low_byte

        # Common unavailable/reserved values.
        if raw_value in (0x0000, 0xFFFF):
            continue

        temperature = (raw_value / 10.0) - 40.0

        if -40.0 <= temperature <= 1200.0:
            return temperature

    raise ValueError(
        f"No valid EGT sensor found in payload: {data}"
    )