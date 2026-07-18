from app.services.raw_obd import RawOBD


obd = RawOBD()

try:
    print("Connecting...")
    obd.connect()
    print("Connected.\n")

    tests = {
        "RPM": 0x0C,
        "Boost control": 0x70,
        "EGT": 0x78,
        "Intake manifold pressure": 0x87,
    }

    for name, pid in tests.items():
        response = obd.pid(pid)
        print(f"{name:28}: {response}")

finally:
    if obd.serial is not None and obd.serial.is_open:
        obd.serial.close()
        print("\nSerial port closed.")