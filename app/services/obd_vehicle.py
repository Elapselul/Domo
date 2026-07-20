import re
import threading
import time

from app.models.vehicle_data import VehicleData
from app.services.pid_decoder import (
    decode_boost,
    decode_coolant,
    decode_egt,
    decode_rpm,
)
from app.services.raw_obd import RawOBD, RawOBDError



class OBDVehicleService:
    def __init__(self):
        self.obd: RawOBD | None = None
        self.running = True
        self.connected = False

        # Values currently displayed by DOMO.
        self.speed = 0.0
        self.rpm = 0.0
        self.battery = 0.0

        self.boost = 0.0
        self.commanded_boost = 0.0
        self.coolant = 0.0
        self.egt = 0.0
        self.trans_temp = 0.0
        self.oil_pressure = 0.0
        self.iat = 0.0
        self.map = 0.0
        self.maf = 0.0

        # Your idle MAP reading was approximately 103 kPa.
        # This is subtracted from absolute pressure to display gauge PSI.
        self.atmospheric_kpa = 103.0

        # RPM and boost are polled quickly.
        # Temperatures and voltage are polled more slowly so they do not
        # interrupt the responsive gauges.
        self._last_temperature_poll = 0.0
        self._last_battery_poll = 0.0

        self._coolant_supported: bool | None = None
        self._egt_supported: bool | None = None
        
        self.thread = threading.Thread(
            target=self._obd_loop,
            daemon=True,
        )
        self.thread.start()

    def _connect(self) -> bool:
        print("DOMO: Connecting to OBDLink...")

        try:
            self.obd = RawOBD()
            self.obd.connect()

            # Allow the CAN connection to settle before requesting PIDs.
            time.sleep(1.0)

            self.connected = True
            print("DOMO: Live vehicle connection ready")
            return True

        except Exception as error:
            print(f"DOMO: Connection failed: {error}")

            self.connected = False

            if self.obd is not None:
                self.obd.close()

            self.obd = None
            return False

    def _read_battery_voltage(self) -> float | None:
        """
        Read adapter/vehicle voltage using the ELM command ATRV.

        Typical response:
            14.2V
        """
        if self.obd is None:
            return None

        try:
            response = self.obd.send_raw("ATRV")

            match = re.search(
                r"(\d+(?:\.\d+)?)\s*V",
                response,
                re.IGNORECASE,
            )

            if match is None:
                return None

            return float(match.group(1))

        except Exception as error:
            print(f"DOMO: Battery read failed: {error}")
            return None

    def _read_temperature_values(self) -> None:
        if self.obd is None:
            return

        # Coolant — Mode 01 PID 05
        if self._coolant_supported is not False:
            try:
                payload = self.obd.pid(0x05)

                print(f"Coolant payload: {payload}")

                coolant = decode_coolant(payload)

                # Reject obviously invalid readings before putting them
                # on the dashboard.
                if -40.0 <= coolant <= 215.0:
                    self.coolant = coolant
                    self._coolant_supported = True

                    print(f"Coolant: {self.coolant:.1f} °C")

            except Exception as error:
                print(f"DOMO: Coolant read failed: {error}")

                # Leave this as None while testing. Some temporary ECU
                # communication errors can look like unsupported PIDs.

        # EGT bank 1 — Mode 01 PID 78
        if self._egt_supported is not False:
            try:
                payload = self.obd.pid(0x78)

                print(f"EGT payload: {payload}")

                egt = decode_egt(payload)

                if -40.0 <= egt <= 1200.0:
                    self.egt = egt
                    self._egt_supported = True

                    print(f"EGT: {self.egt:.1f} °C")

            except Exception as error:
                print(f"DOMO: EGT read failed: {error}")

    def _read_live_values(self) -> None:
        if self.obd is None:
            return

        current_time = time.monotonic()

        # RPM — fast polling
        try:
            rpm_payload = self.obd.pid(0x0C)
            self.rpm = decode_rpm(rpm_payload)

        except Exception as error:
            print(f"DOMO: RPM read failed: {error}")

        # Boost — fast polling
        try:
            boost_payload = self.obd.pid(0x70)

            boost_data = decode_boost(
                boost_payload,
                atmospheric_kpa=self.atmospheric_kpa,
            )

            self.boost = max(
                0.0,
                boost_data.actual_psi_gauge,
            )

            self.commanded_boost = max(
                0.0,
                boost_data.commanded_psi_gauge,
            )

        except Exception as error:
            print(f"DOMO: Boost read failed: {error}")

        # Coolant and EGT — twice per second.
        if current_time - self._last_temperature_poll >= 0.5:
            self._last_temperature_poll = current_time
            self._read_temperature_values()

        # Battery — once every two seconds.
        if current_time - self._last_battery_poll >= 2.0:
            self._last_battery_poll = current_time

            battery = self._read_battery_voltage()

            if battery is not None:
                self.battery = battery

    def _obd_loop(self) -> None:
        # Let the Pi, OBDLink and vehicle ECU finish waking up.
        print("DOMO: Waiting for vehicle systems...")
        time.sleep(2)

        while self.running:
            if not self.connected or self.obd is None:
                if not self._connect():
                    time.sleep(3)
                    continue

            try:
                self._read_live_values()

            except RawOBDError as error:
                print(f"DOMO: OBD connection lost: {error}")
                self._disconnect()
                time.sleep(2)

            except Exception as error:
                print(f"DOMO: Vehicle loop error: {error}")

            time.sleep(0.05)

    def _disconnect(self) -> None:
        self.connected = False

        if self.obd is not None:
            self.obd.close()

        self.obd = None

    def get_data(self) -> VehicleData:
        return VehicleData(
            speed=self.speed,
            rpm=self.rpm,
            battery=self.battery,

            boost=self.boost,
            commanded_boost=self.commanded_boost,
            coolant=self.coolant,
            egt=self.egt,
            trans_temp=self.trans_temp,
            oil_pressure=self.oil_pressure,
            iat=self.iat,
            map=self.map,
            maf=self.maf,
        )

    def close(self) -> None:
        self.running = False
        self._disconnect()