from flask import Flask, render_template_string

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GPS Tracker</title>

    <link
        rel="stylesheet"
        href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    >

    <style>
        * { box-sizing: border-box; }
        html, body { height: 100%; margin: 0; }
        body {
            background: #eef3f8;
            color: #17202a;
            font-family: Arial, Helvetica, sans-serif;
        }
        header {
            padding: 18px;
            color: white;
            background: linear-gradient(135deg, #1769aa, #2196f3);
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
        }
        header h1 { margin: 0; font-size: 28px; }
        header p { margin: 6px 0 0; opacity: 0.9; }
        .control-panel {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 12px;
            background: white;
            border-bottom: 1px solid #d8e0e8;
        }
        #status {
            min-width: 250px;
            color: #46515c;
            font-size: 14px;
            text-align: center;
        }
        #status.success { color: #16803c; }
        #status.error { color: #c62828; }
        button {
            padding: 10px 16px;
            border: 0;
            border-radius: 6px;
            color: white;
            background: #1976d2;
            font-size: 14px;
            cursor: pointer;
            transition: background 0.2s ease, transform 0.2s ease;
        }
        button:hover {
            background: #125ca3;
            transform: translateY(-1px);
        }
        button:disabled {
            background: #9eabb7;
            cursor: not-allowed;
            transform: none;
        }
        button.stop { background: #d32f2f; }
        button.stop:hover { background: #a92323; }
        .information {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            padding: 10px;
            background: #f8fafc;
        }
        .info-card {
            padding: 10px;
            border: 1px solid #dce5ed;
            border-radius: 6px;
            background: white;
            text-align: center;
        }
        .info-label {
            display: block;
            margin-bottom: 5px;
            color: #667784;
            font-size: 12px;
        }
        .info-value {
            color: #17202a;
            font-size: 15px;
            font-weight: bold;
        }
        #map {
            width: 100%;
            height: calc(100vh - 245px);
            min-height: 400px;
        }
        @media (max-width: 650px) {
            header h1 { font-size: 23px; }
            .information { grid-template-columns: 1fr; }
            #map { height: calc(100vh - 350px); }
        }
    </style>
</head>

<body>
    <header>
        <h1>Online GPS Tracker</h1>
        <p>View your current location on the map</p>
    </header>

    <section class="control-panel">
        <div id="status">GPS tracking is stopped.</div>

        <button id="startButton" onclick="startTracking()">
            Start Tracking
        </button>

        <button id="stopButton" class="stop" onclick="stopTracking()" disabled>
            Stop Tracking
        </button>

        <button onclick="centerOnLocation()">Center Map</button>
    </section>

    <section class="information">
        <div class="info-card">
            <span class="info-label">Latitude</span>
            <span id="latitude" class="info-value">--</span>
        </div>

        <div class="info-card">
            <span class="info-label">Longitude</span>
            <span id="longitude" class="info-value">--</span>
        </div>

        <div class="info-card">
            <span class="info-label">Accuracy</span>
            <span id="accuracy" class="info-value">--</span>
        </div>
    </section>

    <div id="map"></div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <script>
        let map;
        let marker = null;
        let accuracyCircle = null;
        let watchId = null;
        let latestLocation = null;

        const statusElement = document.getElementById("status");
        const startButton = document.getElementById("startButton");
        const stopButton = document.getElementById("stopButton");

        map = L.map("map").setView([0, 0], 2);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution: "&copy; OpenStreetMap contributors"
        }).addTo(map);

        function setStatus(message, type = "") {
            statusElement.textContent = message;
            statusElement.className = type;
        }

        function startTracking() {
            if (!navigator.geolocation) {
                setStatus("Geolocation is not supported by this browser.", "error");
                return;
            }

            if (watchId !== null) {
                return;
            }

            setStatus("Requesting your GPS location...", "");

            startButton.disabled = true;
            stopButton.disabled = false;

            watchId = navigator.geolocation.watchPosition(
                updateLocation,
                locationError,
                {
                    enableHighAccuracy: true,
                    maximumAge: 5000,
                    timeout: 15000
                }
            );
        }

        function stopTracking() {
            if (watchId !== null) {
                navigator.geolocation.clearWatch(watchId);
                watchId = null;
            }

            startButton.disabled = false;
            stopButton.disabled = true;
            setStatus("GPS tracking is stopped.", "");
        }

        function updateLocation(position) {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            const accuracy = position.coords.accuracy;

            latestLocation = {
                latitude,
                longitude,
                accuracy
            };

            document.getElementById("latitude").textContent = latitude.toFixed(6);
            document.getElementById("longitude").textContent = longitude.toFixed(6);
            document.getElementById("accuracy").textContent = accuracy.toFixed(1) + " meters";

            setStatus("GPS location updated.", "success");

            const mapLocation = [latitude, longitude];

            if (marker === null) {
                marker = L.marker(mapLocation)
                    .addTo(map)
                    .bindPopup("<b>You are here</b>")
                    .openPopup();

                accuracyCircle = L.circle(mapLocation, {
                    radius: accuracy,
                    color: "#1976d2",
                    weight: 2,
                    fillColor: "#64b5f6",
                    fillOpacity: 0.25
                }).addTo(map);

                map.setView(mapLocation, 16);
            } else {
                marker.setLatLng(mapLocation);
                accuracyCircle.setLatLng(mapLocation);
                accuracyCircle.setRadius(accuracy);
            }
        }

        function locationError(error) {
            let message = "Unable to get your location.";

            if (error.code === error.PERMISSION_DENIED) {
                message = "Location permission was denied. Allow location access and try again.";
            } else if (error.code === error.POSITION_UNAVAILABLE) {
                message = "Your location is currently unavailable.";
            } else if (error.code === error.TIMEOUT) {
                message = "The GPS request timed out. Try again.";
            }

            setStatus(message, "error");
            startButton.disabled = false;
            stopButton.disabled = true;

            if (watchId !== null) {
                navigator.geolocation.clearWatch(watchId);
                watchId = null;
            }
        }

        function centerOnLocation() {
            if (latestLocation === null) {
                setStatus("No GPS location is available yet.", "error");
                return;
            }

            const location = [
                latestLocation.latitude,
                latestLocation.longitude
            ];

            map.setView(location, 17);

            if (marker !== null) {
                marker.openPopup();
            }
        }

        startTracking();
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)