from app.services.raw_obd import RawOBD, RawOBDError


obd = RawOBD()

tests = {
    "RPM": 0x0C,
    "Boost control": 0x70,
    "EGT": 0x78,
    "Intake manifold pressure": 0x87,
}

try:
    print("Connecting...")
    obd.connect()
    print()

    for name, pid in tests.items():
        try:
            payload = obd.pid(pid)

            print(
                f"{name:28}: "
                f"{payload.hex(' ').upper()}"
            )

        except RawOBDError as error:
            print(f"{name:28}: ERROR — {error}")

finally:
    obd.close()
    print("\nSerial port closed.")