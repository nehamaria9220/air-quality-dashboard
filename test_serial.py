import time
import random
from serial_reader import parse_serial_line


def generate_message():
    # Generate a simulated sensor reading
    raw = random.randint(500, 2000)
    voltage = int(raw * 3300 / 4095)
    sensor_voltage = voltage * 2

    # Temporary simulation logic, not the actual hardware threshold
    fan = 1 if sensor_voltage >= 2000 else 0
    buzzer = 1 if sensor_voltage >= 2000 else 0

    return (
        f"RAW:{raw},VOLTAGE:{voltage},"
        f"SENSOR:{sensor_voltage},FAN:{fan},BUZZER:{buzzer}"
    )


while True:
    message = generate_message()

    print("Received:", message)

    result = parse_serial_line(message)

    if result is not None:
        print("Parsed:", result)

    print("-" * 40)

    time.sleep(1)