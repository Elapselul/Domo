from collections import deque
from copy import copy


class DataLogger:
    def __init__(self, max_samples=1000):
        self.samples = deque(maxlen=max_samples)

    def add_sample(self, vehicle_data):
        self.samples.append(copy(vehicle_data))

    def clear(self):
        self.samples.clear()

    def get_samples(self):
        return list(self.samples)

    def get_latest(self, count=100):
        if count <= 0:
            return []

        return list(self.samples)[-count:]

    def __len__(self):
        return len(self.samples)