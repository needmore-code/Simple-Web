#!/usr/bin/env python3
"""Simple Web Browser - Fast & Privacy-Focused"""

import sys
from PyQt6.QtWidgets import QApplication
from src.ui.browser_window import BrowserWindow

def main():
    app = QApplication(sys.argv)
    browser = BrowserWindow()
    browser.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
