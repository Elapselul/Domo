import random


class FakeCarData:
    def __init__(self):
        self.speed = 0
        self.rpm = 800
        self.boost = 0.0
        self.coolant = 82
        self.battery = 14.1

    def move_towards(self, current, target, amount):
        if current < target:
            return min(current + amount, target)
        if current > target:
            return max(current - amount, target)
        return current

    def get_data(self):
        self.speed = self.move_towards(self.speed, random.randint(0, 110), 3)
        self.rpm = self.move_towards(self.rpm, random.randint(750, 3800), 120)
        self.boost = self.move_towards(self.boost, random.uniform(0, 24), 0.8)
        self.coolant = self.move_towards(self.coolant, random.randint(78, 98), 0.2)
        self.battery = self.move_towards(self.battery, random.uniform(12.4, 14.5), 0.1)

        return {
            "speed": int(self.speed),
            "rpm": int(self.rpm),
            "boost": round(self.boost, 1),
            "coolant": int(self.coolant),
            "battery": round(self.battery, 1),
            "iat": int(random.randint(25, 55)),
            "map": int(random.randint(100, 260)),
            "maf": int(random.randint(20, 160)),
            "commanded_boost": round(random.uniform(0, 22), 1),

        }