from flask import Flask, Response
import csv
import os
import requests
import re

# Configuration for the log file and Libre Hardware Monitor API
LOG_FILE = "C:/path/to/monitoring.csv"  # Ensure correct path
LIBRE_HW_URL = "http://YOUR.GAMING.MACHINE.IP:8085/data.json"  # Libre Hardware Monitor API Endpoint
PORT = 9187  # Prometheus exporter port, change if needed

# Initialize Flask app
app = Flask(__name__)

def fetch_sensors():
    """Fetch and parse sensor data from Libre Hardware Monitor"""
    try:
        response = requests.get(LIBRE_HW_URL, timeout=5)
        response.raise_for_status()  # Raise error for HTTP issues
        return response.json()
    except requests.RequestException as e:
        print(f"ERROR: Failed to fetch Libre Hardware Monitor data: {e}")
        return None

def sanitize_name(name):
    """Convert sensor names to valid Prometheus metric names"""
    name = name.lower().replace(" ", "_").replace("-", "_")
    name = re.sub(r'[^a-zA-Z0-9_]', '', name)  # Remove invalid characters
    return name

def parse_sensors(sensor_data, parent=""):
    """Recursively extract numeric sensor values"""
    metrics = []
    if "Children" in sensor_data:
        for sensor in sensor_data["Children"]:
            sensor_name = sanitize_name(sensor.get("Text", "unknown"))
            full_name = f"{parent}_{sensor_name}" if parent else sensor_name

            if "Value" in sensor and sensor["Value"]:
                try:
                    # Extract only numeric values (ignore units like "V", "°C")
                    value = re.sub(r'[^\d,.-]', '', sensor["Value"]).replace(",", ".")
                    value = float(value)  # Convert to float

                    # Append valid Prometheus metric
                    metrics.append(f"libre_hw_{full_name} {value}")
                except ValueError:
                    pass  # Ignore non-numeric values

            # Recursively process children
            metrics.extend(parse_sensors(sensor, full_name))

    return metrics

def get_fps():
    """Reads the last valid FPS value from RTSS log file."""
    if not os.path.exists(LOG_FILE):
        print("Log file not found!")
        return None

    try:
        with open(LOG_FILE, "r", encoding="utf-8-sig", errors="replace") as file:
            reader = csv.reader(file)
            rows = list(reader)

            # Find the last valid FPS row
            for row in reversed(rows):
                if len(row) >= 2:  # Ensure there are at least two columns
                    fps_value = row[-1].strip()  # Assuming FPS is the last column

                    # Check if FPS is numeric and not "N/A"
                    if fps_value.replace(".", "", 1).isdigit():
                        return float(fps_value)
    except Exception as e:
        print(f"Error reading file: {e}")

    return None  # Return None if no valid data found

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    # Fetch Libre Hardware Monitor sensor data
    sensor_data = fetch_sensors()
    metrics = []

    if not sensor_data:
        metrics.append("# ERROR: Failed to fetch Libre Hardware Monitor data")

    else:
        # Parse Libre Hardware Monitor sensors and append to metrics
        metrics.extend(parse_sensors(sensor_data))

    # Get FPS data from log file and append to metrics
    fps = get_fps()
    if fps is None:
        fps = 0.0  # Default FPS if no data available

    # Add FPS data to the metrics
    metrics.append(f"# HELP rtss_fps Current FPS from RTSS")
    metrics.append(f"# TYPE rtss_fps gauge")
    metrics.append(f"rtss_fps {fps}")

    # Return the complete metrics to Prometheus
    return Response("\n".join(metrics), mimetype="text/plain")

if __name__ == '__main__':
    print(f"Starting Combined Exporter on http://0.0.0.0:{PORT}/metrics")
    app.run(host='0.0.0.0', port=PORT)
