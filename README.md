# Simple-Web

A collection of Python projects showcasing web and graphics development with Python.

## Overview

Simple-Web contains five distinct Python projects:

1. **3D Flight Simulator** - A realistic flight simulation with physics-based aircraft dynamics
2. **PyChromium Browser** - A lightweight web browser built with PyQt5
3. **Simple Website** - A Flask project hub that lists and links to the repository's apps
4. **Messaging App** - A Flask + Socket.IO chat app with login, direct messaging, and group chats
5. **GPS Tracker** - An interactive real-time GPS tracking application with live map updates

## Projects

### 🛩️ 3D Flight Simulator (`3d_Flight_Sim.py`)

A feature-rich 3D flight simulator built with OpenGL and Pygame that includes:

- **Realistic Aircraft Physics**
  - Aerodynamic lift and drag calculations
  - Thrust and gravity simulation
  - Angle of attack computation
  - Propulsion system modeling

- **Advanced Flight Controls**
  - Pitch, roll, and yaw control
  - Throttle management
  - Orientation represented as Euler angles
  - Smooth flight dynamics

- **Visual Features**
  - 3D aircraft model with fuselage, wings, and tail
  - Procedurally generated terrain
  - Sky dome rendering
  - Real-time camera following the aircraft

- **Gameplay**
  - Altitude and speed monitoring
  - Terrain collision detection
  - Aircraft state management

**Requirements:**
- pygame
- PyOpenGL
- numpy

**Controls:**
- `W/S` - Pitch up/down
- `A/D` - Roll left/right
- `Q/E` - Yaw left/right
- `↑/↓` - Increase/decrease throttle
- `R` - Reset aircraft
- `ESC` - Exit

### 🌐 PyChromium Browser (`py_chromium_browser.py`)

A multi-tab web browser built with PyQt5 and Chromium engine featuring:

- **Tab Management**
  - Open multiple tabs simultaneously
  - Close tabs (minimum one tab required)
  - Tab switching with title updates

- **Navigation**
  - Back and forward buttons
  - Page reload functionality
  - Home button (defaults to Google)
  - URL bar with auto-formatting

- **User Experience**
  - Loading progress indicator
  - Load status feedback
  - Responsive toolbar navigation
  - Clean, intuitive interface

**Requirements:**
- PyQt5
- PyQtWebEngine

**Usage:**
```bash
python py_chromium_browser.py
```

### 📄 Project Hub (`website.py`)

A Flask-powered project hub that serves as the landing page for Simple-Web.

- Displays the repository's applications as responsive project cards
- Shows each project's icon, category, description, run command, and source link
- Groups projects into Desktop app and Web app categories
- Includes a responsive turquoise and blue-green design
- Includes guidance for installing dependencies and running the projects
- Automatically opens `http://localhost:5000` in the default browser
- Runs in Flask debug mode

**Requirements:**
- Flask

**Usage:**
```bash
python website.py
```

The project hub runs at `http://localhost:5000`.

### 💬 Messaging App (`app.py`)

A web-based chat app with account signup/login, group chats, direct messages, SQLite storage, and live updates using Flask-SocketIO.

**Features:**
- User registration and login
- Direct/private messaging
- Group chat creation and membership management
- Real-time message updates without page refresh
- Online presence indicators
- Persistent storage in `chat.db`

**Requirements:**
- Flask
- Flask-Login
- Flask-SocketIO
- Werkzeug

**Install:**
```bash
pip install Flask Flask-Login Flask-SocketIO Werkzeug
```

**Run:**
```bash
python app.py
```

The app listens on `http://0.0.0.0:5000`.

To connect from another device on the same local network, find the host computer's IPv4 address using `ipconfig` on Windows (or `ip addr` on Linux/macOS), then open:

```text
http://<host-ip-address>:5000
```

Both devices must be connected to the same network, and the host firewall must allow TCP traffic on port `5000`.

### 📍 GPS Tracker (`gps.py`)

An interactive real-time GPS tracking application with live map visualization using Leaflet.js and the Geolocation API.

**Features:**
- Real-time GPS location tracking with high accuracy mode
- Interactive map display powered by OpenStreetMap
- Live location marker and accuracy radius visualization
- Start/stop tracking controls
- Display latitude, longitude, and accuracy metrics
- Center map on current location button
- Responsive design for mobile and desktop
- Geolocation permission handling

**Requirements:**
- Flask

**Usage:**
```bash
python gps.py
```

The app listens on `http://0.0.0.0:5000` and the browser asks for GPS permission when tracking starts.

**Browser Compatibility:**
- Requires HTTPS or localhost to use the Geolocation API
- Works on modern browsers with geolocation support
- Mobile-friendly interface for on-the-go tracking

To connect from another device, use the host computer's IPv4 address:
```text
http://<host-ip-address>:5000
```

## Installation

Clone the repository:
```bash
git clone https://github.com/needmore-code/Simple-Web.git
cd Simple-Web
```

Install dependencies:
```bash
pip install pygame PyOpenGL numpy PyQt5 PyQtWebEngine Flask Flask-Login Flask-SocketIO Werkzeug
```

## Usage

Run any project individually:

```bash
# Flight Simulator
python 3d_Flight_Sim.py

# Web Browser
python py_chromium_browser.py

# Project Hub
python website.py

# Messaging App
python app.py

# GPS Tracker
python gps.py
```

## Author

Created by [needmore-code](https://github.com/needmore-code)

---

**Note:** Each script is designed to be run independently. Ensure you have Python 3.x installed along with the required dependencies for each project.
