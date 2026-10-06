from flask import Flask, render_template, jsonify
import random

from serial_reader import parse_serial_line

app = Flask(__name__)


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


def generate_serial_message():
    # Simulate the percentage change calculated by the real firmware
    change_percent = random.randint(0, 220)

    # Determine air-quality category exactly like the firmware
    if change_percent <= 30:
        air_quality = "GOOD"
    elif change_percent <= 70:
        air_quality = "MODERATE"
    elif change_percent <= 150:
        air_quality = "POOR"
    else:
        air_quality = "HAZARDOUS"

    # Generate realistic-looking test values for the other fields
    raw = random.randint(10, 40)
    voltage = int(raw * 3300 / 4095)
    sensor_voltage = voltage * 2

    # Produce exactly the same format as the NXP firmware
    return (
        f"Raw: {raw} | "
        f"Change: {change_percent}% | "
        f"Air: {air_quality} | "
        f"ADC: {voltage} mV | "
        f"Sensor AO: {sensor_voltage} mV"
    )


@app.route("/data")
def data():
    message = generate_serial_message()

    sensor_data = parse_serial_line(message)

    if sensor_data is None:
        return jsonify({
            "error": "Invalid sensor data"
        }), 500

    return jsonify({
        "air_quality": sensor_data["air_score"],
        "air_score": sensor_data["air_score"],
        "status": sensor_data["air_quality"],
        "change_percent": sensor_data["change_percent"],
        "fan": sensor_data["fan"],
        "alert": sensor_data["alert"],
        "raw_value": sensor_data["raw_value"],
        "sensor_voltage": sensor_data["sensorVoltage_mV"]
    })


if __name__ == "__main__":
    app.run(debug=True)