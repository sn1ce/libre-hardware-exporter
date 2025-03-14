from flask import Flask, Response
import csv
import os

# Configuration
LOG_FILE = "C:/tooling/dashboarding/gpu_monitoring.csv"  # Ensure correct path
PORT = 9187  # Prometheus exporter port

app = Flask(__name__)

def get_fps():
    """Reads the last valid FPS value from RTSS log file."""
    if not os.path.exists(LOG_FILE):
        print("Log file not found!")
        return None

    try:
        with open(LOG_FILE, "r", encoding="utf-8-sig", errors="replace") as file:
            reader = csv.reader(file)
            rows = list(reader)

            # DEBUG: Print last 5 rows to analyze structure
            print("Last 5 rows:")
            for row in rows[-5:]:
                print(row)

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

@app.route("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    fps = get_fps()
    if fps is None:
        fps = 0.0  # Default FPS if no data available

    metrics = f"""# HELP rtss_fps Current FPS from RTSS
# TYPE rtss_fps gauge
rtss_fps {fps}
"""
    return Response(metrics, mimetype="text/plain")

if __name__ == "__main__":
    print(f"Starting RTSS FPS Exporter on http://0.0.0.0:{PORT}/metrics")
    app.run(host="0.0.0.0", port=PORT)
