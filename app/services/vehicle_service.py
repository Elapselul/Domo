from app.services.simulator import FakeCarData


class VehicleService:
    def __init__(self):
        self.data_source = FakeCarData()

    def get_current_data(self):
        return self.data_source.get_data()