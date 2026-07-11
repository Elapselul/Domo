from dataclasses import dataclass


@dataclass
class VehicleData:
    speed: int
    rpm: int
    boost: float
    commanded_boost: float
    coolant: int
    battery: float
    egt: int
    trans_temp: int
    oil_pressure: int
    iat: int
    map: int
    maf: int