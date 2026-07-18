from app.services.simulator import FakeCarData
from app.services.obd_vehicle import OBDVehicleService


USE_SIMULATOR = False


class VehicleService:
    def __init__(self):
        if USE_SIMULATOR:
            print("DOMO: Simulator mode")
            self.data_source = FakeCarData()
        else:
            print("DOMO: Live vehicle mode")
            self.data_source = OBDVehicleService()

    def get_current_data(self):
        return self.data_source.get_data()