def parse_serial_line(line):
    """
    Parse serial output from the FRDM-MCXN236.

    Expected format:
    Raw: 1234 | Change: 50% | Air: MODERATE | ADC: 994 mV | Sensor AO: 1988 mV
    """

    try:
        parts = line.strip().split("|")

        if len(parts) != 5:
            return None

        raw_value = int(parts[0].split(":")[1].strip())

        change_text = parts[1].split(":")[1].strip()
        change_percent = int(change_text.replace("%", ""))

        air_quality = parts[2].split(":")[1].strip()

        adc_text = parts[3].split(":")[1].strip()
        voltage_mV = int(adc_text.replace("mV", "").strip())

        sensor_text = parts[4].split(":")[1].strip()
        sensor_voltage_mV = int(
            sensor_text.replace("mV", "").strip()
        )

        # Same score calculation used by the firmware
        if change_percent >= 200:
            air_score = 0
        else:
            air_score = 100 - (change_percent // 2)

        # Same fan/buzzer condition used by the firmware
        fan = change_percent > 70
        alert = change_percent > 70

        return {
            "raw_value": raw_value,
            "change_percent": change_percent,
            "air_quality": air_quality,
            "air_score": air_score,
            "voltage_mV": voltage_mV,
            "sensorVoltage_mV": sensor_voltage_mV,
            "fan": fan,
            "alert": alert
        }

    except (ValueError, IndexError):
        return None


if __name__ == "__main__":

    test_messages = [
        "Raw: 12 | Change: 0% | Air: GOOD | ADC: 9 mV | Sensor AO: 18 mV",
        "Raw: 18 | Change: 50% | Air: MODERATE | ADC: 14 mV | Sensor AO: 28 mV",
        "Raw: 24 | Change: 100% | Air: POOR | ADC: 19 mV | Sensor AO: 38 mV",
        "Raw: 36 | Change: 200% | Air: HAZARDOUS | ADC: 29 mV | Sensor AO: 58 mV",
        "OLED loop update status = 0"
    ]

    for message in test_messages:
        result = parse_serial_line(message)
        print(result)