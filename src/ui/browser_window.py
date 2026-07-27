"""Main browser window"""

from PyQt6.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLineEdit, QPushButton, QTextEdit, QLabel
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from src.core.engine import BrowserEngine
import logging

logger = logging.getLogger(__name__)

class BrowserWindow(QMainWindow):
    """Main browser window"""
    
    def __init__(self):
        super().__init__()
        self.engine = BrowserEngine()
        self.init_ui()
        self.setup_privacy()
        
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Simple Web Browser")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Navigation bar
        nav_layout = QHBoxLayout()
        
        # Back button
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.go_back)
        nav_layout.addWidget(self.back_btn)
        
        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL...")
        self.url_bar.returnPressed.connect(self.load_url)
        nav_layout.addWidget(self.url_bar)
        
        # Go button
        self.go_btn = QPushButton("Go")
        self.go_btn.clicked.connect(self.load_url)
        nav_layout.addWidget(self.go_btn)
        
        # Privacy button
        self.privacy_btn = QPushButton("🔒 Clear Cookies")
        self.privacy_btn.clicked.connect(self.clear_data)
        nav_layout.addWidget(self.privacy_btn)
        
        main_layout.addLayout(nav_layout)
        
        # Web view
        self.web_view = QWebEngineView()
        main_layout.addWidget(self.web_view)
        
        # Status bar
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
        
        self.setCentralWidget(central_widget)
    
    def setup_privacy(self):
        """Configure privacy settings"""
        profile = QWebEngineProfile()
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        self.web_view.page().setWebEngineProfile(profile)
    
    def load_url(self):
        """Load URL from address bar"""
        url = self.url_bar.text().strip()
        if not url:
            return
        
        self.status_label.setText(f"Loading {url}...")
        result = self.engine.load_page(url)
        
        if result['success']:
            self.url_bar.setText(result['url'])
            self.web_view.setHtml(result['html'], self.web_view.page().baseUrl())
            self.setWindowTitle(f"{result['title']} - Simple Browser")
            self.status_label.setText(f"Loaded: {result['url']}")
        else:
            error_html = f"""
            <html>
            <body style="font-family: Arial; padding: 20px;">
                <h1>Error Loading Page</h1>
                <p>{result['error']}</p>
                <p>URL: {result['url']}</p>
            </body>
            </html>
            """
            self.web_view.setHtml(error_html)
            self.status_label.setText(f"Error: {result['error']}")
    
    def go_back(self):
        """Navigate back"""
        prev_url = self.engine.back()
        if prev_url:
            self.url_bar.setText(prev_url)
            self.load_url()
    
    def clear_data(self):
        """Clear privacy data"""
        self.engine.clear_cookies()
        self.status_label.setText("✓ Cookies cleared")
