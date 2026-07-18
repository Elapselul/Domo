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