# Simple-Web

A collection of Python projects showcasing web applications, desktop apps, and graphical experiments.

## Overview

Simple-Web currently contains six projects:

1. **3D Flight Simulator** — A realistic flight simulator with aircraft physics.
2. **PyChromium Browser** — A multi-tab desktop browser built with PyQt5 and Chromium.
3. **Messaging App** — A Flask and Socket.IO chat app with accounts and private/group chat.
4. **GPS Tracker** — An interactive browser-based real-time location tracker.
5. **AI Chatbot** — A local chatbot powered by Ollama and the OpenAI-compatible API.
6. **Simple Website** — A Flask project hub linking to the repository projects.

## Projects

### 🛩️ 3D Flight Simulator (`3d_Flight_Sim.py`)

A 3D flight simulator built with Pygame, OpenGL, and NumPy.

**Requirements:**
- pygame
- PyOpenGL
- numpy

**Controls:**
- `W/S` — Pitch up/down
- `A/D` — Roll left/right
- `Q/E` — Yaw left/right
- `↑/↓` — Increase/decrease throttle
- `R` — Reset aircraft
- `Esc` — Exit

### 🌐 PyChromium Browser (`py_chromium_browser.py`)

A multi-tab desktop browser built with PyQt5 and PyQtWebEngine.

```bash
pip install PyQt5 PyQtWebEngine
python py_chromium_browser.py
```

### 💬 Messaging App (`app.py`)

A web chat app with registration, login, direct messages, group chats, SQLite storage, and live updates.

```bash
pip install Flask Flask-Login Flask-SocketIO Werkzeug
python app.py
```

The app listens on `http://0.0.0.0:5000`. To access it from another device on the same network, open `http://<host-ipv4-address>:5000` and allow TCP port 5000 through the Windows firewall.

### 📍 GPS Tracker (`gps.py`)

A real-time location tracker using Leaflet.js and the Geolocation API.

```bash
pip install Flask
python gps.py
```

The app listens on `http://0.0.0.0:5000` and asks for GPS permission in the browser.

> Browser compatibility: Geolocation requires HTTPS or localhost. It works on modern browsers with geolocation support and is mobile-friendly.

### 🤖 AI Chatbot (`ai_chatbot.py`)

A Flask chat interface that uses Ollama through an OpenAI-compatible local API. Ollama and model inference run locally, and no real OpenAI API key is required.

**Install Ollama:**

1. Download and install Ollama from <https://ollama.com/download/windows>.
2. Download the model:

```powershell
ollama pull llama3.2:3b
```

3. Start Ollama in its own terminal:

```powershell
ollama serve
```

**Install and run the chatbot:**

```powershell
pip install flask openai
python ai_chatbot.py
```

Open `http://127.0.0.1:5001`.

If Ollama is already running, do not start `ollama serve` again.

### 🧭 Project Hub (`website.py`)

A Flask project hub that shows the repository apps as cards and includes run commands and source links.

```bash
pip install Flask
python website.py
```

The hub automatically opens at `http://localhost:5000`.

## Installation

Clone the repository:

```bash
git clone https://github.com/needmore-code/Simple-Web.git
cd Simple-Web
```

Install dependencies for the project you want to run. Each project is independent and has its own dependencies.

## Usage

Run a project from the repository folder:

```bash
# 3D Flight Simulator
python 3d_Flight_Sim.py

# PyChromium Browser
python py_chromium_browser.py

# Project Hub
python website.py

# Messaging App
python app.py

# GPS Tracker
python gps.py

# AI Chatbot
python ai_chatbot.py
```

Only run one server-based project at a time when using the same port. Stop the current server with `Ctrl+C` before starting another one.

## Author

Created by [needmore-code](https://github.com/needmore-code)

---

**Note:** Each project is independent. Make sure Python 3.x and the dependencies for each project are installed.
