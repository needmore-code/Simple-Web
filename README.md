# Simple Web Browser 🌐

A fast, privacy-focused web browser built in Python, inspired by Firefox.

## Features

✅ **Speed** - Lightweight and optimized HTTP requests  
✅ **Privacy** - No tracking, no cookies by default, local-only storage  
✅ **Simplicity** - Clean, maintainable Python codebase  

## Architecture

- `core/` - Core browser engine
- `ui/` - User interface (GTK/PyQt)
- `network/` - HTTP/HTTPS request handling
- `parser/` - HTML/CSS parsing
- `storage/` - Local data management

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Requirements

- Python 3.10+
- PyQt6 (GUI)
- requests (HTTP)
- beautifulsoup4 (Parsing)
