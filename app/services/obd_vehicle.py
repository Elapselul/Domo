import threading
import time

import obd

from app.models.vehicle_data import VehicleData


class OBDVehicleService:
    def __init__(self):
        self.connection = None
        self.connected = False

        self.rpm = 0.0
        self.speed = 0.0
        self.battery = 0.0

        self._running = True
        self._thread = threading.Thread(
            target=self._worker,
            daemon=True,
        )
        self._thread.start()

    def _connect(self):
        try:
            print("DOMO: Connecting to OBDLink...")

            self.connection = obd.OBD(fast=False)
            self.connected = self.connection.is_connected()

            if self.connected:
                print("DOMO: Vehicle connected")
            else:
                print("DOMO: Vehicle not detected")

        except Exception as error:
            print(f"DOMO: OBD connection error: {error}")
            self.connected = False
            self.connection = None

    def _worker(self):
        while self._running:
            if not self.connected:
                self._connect()
                time.sleep(2)
                continue

            try:
                rpm_response = self.connection.query(
                    obd.commands.RPM
                )
                speed_response = self.connection.query(
                    obd.commands.SPEED
                )
                battery_response = self.connection.query(
                    obd.commands.ELM_VOLTAGE
                )

                if not rpm_response.is_null():
                    self.rpm = float(
                        rpm_response.value.magnitude
                    )

                if not speed_response.is_null():
                    self.speed = float(
                        speed_response.value.magnitude
                    )

                if not battery_response.is_null():
                    self.battery = float(
                        battery_response.value.magnitude
                    )

            except Exception as error:
                print(f"DOMO: OBD read error: {error}")

                self.connected = False

                if self.connection is not None:
                    try:
                        self.connection.close()
                    except Exception:
                        pass

                self.connection = None

            time.sleep(0.1)

    def get_data(self):
        return VehicleData(
            speed=int(self.speed),
            rpm=int(self.rpm),
            boost=0.0,
            commanded_boost=0.0,
            coolant=0,
            battery=round(self.battery, 1),
            egt=0,
            trans_temp=0,
            oil_pressure=0,
            iat=0,
            map=0,
            maf=0,
        )

    def stop(self):
        self._running = False

        if self.connection is not None:
            try:
                self.connection.close()
            except Exception:
                pass