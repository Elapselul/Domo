import time

from app.services.pid_decoder import decode_boost, decode_rpm
from app.services.raw_obd import RawOBD, RawOBDError


obd = RawOBD()

try:
    obd.connect()

    print(
        "RPM     "
        "Commanded abs   Actual abs   "
        "Commanded boost   Actual boost"
    )

    while True:
        rpm_payload = obd.pid(0x0C)
        boost_payload = obd.pid(0x70)

        rpm = decode_rpm(rpm_payload)
        boost = decode_boost(
            boost_payload,
            atmospheric_kpa=103.0,
        )

        print(
            f"{rpm:7.0f} "
            f"{boost.commanded_psi_absolute:12.2f} PSI "
            f"{boost.actual_psi_absolute:10.2f} PSI "
            f"{boost.commanded_psi_gauge:14.2f} PSI "
            f"{boost.actual_psi_gauge:11.2f} PSI"
        )

        time.sleep(0.25)

except KeyboardInterrupt:
    print("\nStopped.")

except RawOBDError as error:
    print(f"\nOBD error: {error}")

finally:
    obd.close()