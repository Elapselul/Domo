import glob
import threading
import time

import obd


from app.models.vehicle_data import VehicleData


class OBDVehicleService:
    def __init__(self):
        self.connection = None
        self.running = True

        self.rpm = 0.0
        self.speed = 0.0
        self.battery = 0.0
        self.throttle = 0.0
        self.engine_load = 0.0

        self.thread = threading.Thread(
            target=self._obd_loop,
            daemon=True,
        )
        self.thread.start()

    def _connect(self):
        import glob

        print("DOMO: Connecting to OBDLink...")

        ports = (
            glob.glob("/dev/ttyUSB*")
            + glob.glob("/dev/ttyACM*")
        )

        if not ports:
            print("DOMO: No USB serial adapter detected")
            self.connection = None
            return False

        for port in ports:
            print(f"DOMO: Trying {port}")

            try:
                connection = obd.OBD(
                    portstr=port,
                    baudrate=None,
                    fast=False,
                    timeout=5,
                )

                if connection.is_connected():
                    self.connection = connection
                    print(f"DOMO: Vehicle connected on {port}")
                    return True

                connection.close()

            except Exception as error:
                print(f"DOMO: Failed on {port}: {error}")

        print("DOMO: Vehicle not detected")
        self.connection = None
        return False

    def _read_value(self, command, unit=None):
        if self.connection is None:
            return None

        try:
            if not self.connection.supports(command):
                return None

            response = self.connection.query(command)

            if response.is_null() or response.value is None:
                return None

            if unit is not None:
                return float(response.value.to(unit).magnitude)

            return float(response.value.magnitude)

        except Exception as error:
            print(f"DOMO: Failed reading {command.name}: {error}")
            return None

    def _obd_loop(self):
        while self.running:
            if self.connection is None or not self.connection.is_connected():
                if not self._connect():
                    time.sleep(3)
                    continue

            rpm = self._read_value(
                obd.commands.RPM,
                "rpm",
            )

            speed = self._read_value(
                obd.commands.SPEED,
                "km/h",
            )

            battery = self._read_value(
                obd.commands.ELM_VOLTAGE,
                "volt",
            )

            throttle = self._read_value(
                obd.commands.THROTTLE_POS,
                "percent",
            )

            engine_load = self._read_value(
                obd.commands.ENGINE_LOAD,
                "percent",
            )

            if rpm is not None:
                self.rpm = rpm

            if speed is not None:
                self.speed = speed

            if battery is not None:
                self.battery = battery

            if throttle is not None:
                self.throttle = throttle

            if engine_load is not None:
                self.engine_load = engine_load

            time.sleep(0.15)

    def get_data(self):
        return VehicleData(
            speed=self.speed,
            rpm=self.rpm,
            battery=self.battery,

            boost=0.0,
            commanded_boost=0.0,
            coolant=0.0,
            egt=0.0,
            trans_temp=0.0,
            oil_pressure=0.0,
            iat=0.0,
            map=0.0,
            maf=0.0,

        )

    def close(self):
        self.running = False

        if self.connection is not None:
            self.connection.close()