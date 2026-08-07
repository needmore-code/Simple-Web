# Simple-Web

A collection of Python projects showcasing web and graphics development with Python.

## Overview

Simple-Web contains three distinct Python projects:

1. **3D Flight Simulator** - A realistic flight simulation with physics-based aircraft dynamics
2. **PyChromium Browser** - A lightweight web browser built with PyQt5
3. **Simple Website** - A basic Flask web server with a styled homepage

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
- `Space` - Pause/resume
- `I` - Toggle debug info
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

### 📄 Simple Website (`website.py`)

A basic Flask web server that serves a styled homepage.

- **Features**
  - Single-page application
  - Turquoise background design
  - Centered content container
  - Auto-opens in default browser
  - Debug mode enabled

**Requirements:**
- Flask
- MarkupSafe

**Usage:**
```bash
python website.py
```

The server runs on `http://localhost:5000` and will automatically open in your default browser.

## Installation

Clone the repository:
```bash
git clone https://github.com/needmore-code/Simple-Web.git
cd Simple-Web
```

Install dependencies:
```bash
pip install pygame PyOpenGL numpy PyQt5 PyQtWebEngine Flask MarkupSafe
```

## Usage

Run any project individually:

```bash
# Flight Simulator
python 3d_Flight_Sim.py

# Web Browser
python py_chromium_browser.py

# Website
python website.py
```

## License

This project is open source. Feel free to use, modify, and distribute as needed.

## Author

Created by [needmore-code](https://github.com/needmore-code)

---

**Note:** Each script is designed to be run independently. Ensure you have Python 3.x installed along with the required dependencies for each project.
