from flask import Flask, Response
import requests
import time
import re

# Libre Hardware Monitor API Endpoint
LIBRE_HW_URL = "http://10.0.0.88:8085/data.json"

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

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    sensor_data = fetch_sensors()
    if not sensor_data:
        return Response("# ERROR: Failed to fetch Libre Hardware Monitor data", mimetype='text/plain')

    metrics = parse_sensors(sensor_data)
    return Response("\n".join(metrics), mimetype='text/plain')

if __name__ == '__main__':
    print("Starting Libre Hardware Monitor Exporter on http://0.0.0.0:9187/metrics")
    app.run(host='0.0.0.0', port=9187)
