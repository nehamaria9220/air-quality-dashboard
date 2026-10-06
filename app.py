from flask import Flask, render_template, jsonify
import serial
import threading

from serial_reader import parse_serial_line

app = Flask(__name__)

# -----------------------------
# Serial connection settings
# -----------------------------

SERIAL_PORT = "COM6"
BAUD_RATE = 115200

latest_sensor_data = None
serial_status = "Connecting..."


# -----------------------------
# Read data from FRDM-MCXN236
# -----------------------------

def read_serial():
    global latest_sensor_data
    global serial_status

    try:
        with serial.Serial(
            SERIAL_PORT,
            BAUD_RATE,
            timeout=1
        ) as ser:

            serial_status = "Connected"

            print(
                f"Connected to FRDM-MCXN236 on {SERIAL_PORT}"
            )

            while True:

                line = (
                    ser.readline()
                    .decode("utf-8", errors="ignore")
                    .strip()
                )

                if not line:
                    continue

                # Show incoming board output in terminal
                print(line)

                # Parser automatically ignores
                # OLED/debug messages
                sensor_data = parse_serial_line(line)

                if sensor_data is not None:
                    latest_sensor_data = sensor_data

    except serial.SerialException as error:

        serial_status = f"Serial error: {error}"

        print(serial_status)


# -----------------------------
# Dashboard
# -----------------------------

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


# -----------------------------
# Sensor API
# -----------------------------

@app.route("/data")
def data():

    if latest_sensor_data is None:

        return jsonify({
            "error": "Waiting for sensor data",
            "connection": serial_status
        }), 503


    sensor_data = latest_sensor_data

    return jsonify({

        "air_quality":
            sensor_data["air_score"],

        "air_score":
            sensor_data["air_score"],

        "status":
            sensor_data["air_quality"],

        "change_percent":
            sensor_data["change_percent"],

        "fan":
            sensor_data["fan"],

        "alert":
            sensor_data["alert"],

        "raw_value":
            sensor_data["raw_value"],

        "sensor_voltage":
            sensor_data["sensorVoltage_mV"],

        "connection":
            serial_status
    })


# -----------------------------
# Start application
# -----------------------------

if __name__ == "__main__":

    serial_thread = threading.Thread(
        target=read_serial,
        daemon=True
    )

    serial_thread.start()

    app.run(
        debug=True,
        use_reloader=False
    )