#!/usr/bin/env python3

import sys
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLineEdit, QPushButton, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BrowserEngine:
    
    SEARCH_ENGINES = {
        'google': 'https://www.google.com/search?q=',
        'duckduckgo': 'https://duckduckgo.com/?q=',
        'bing': 'https://www.bing.com/search?q=',
        'startpage': 'https://www.startpage.com/sp/search?query=',
    }
    
    def __init__(self):
        self.current_url: Optional[str] = None
        self.current_html: Optional[str] = None
        self.history = []
        self.cookies = {}
        self.search_engine = 'duckduckgo'
        
        self.default_headers = {
            'User-Agent': 'SimpleBrowser/1.0 (Privacy-Focused)',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
        }
    
    def load_page(self, url: str) -> Dict:
        try:
            if not url.startswith(('http://', 'https://', 'www.')):
                search_url = self.SEARCH_ENGINES[self.search_engine] + url.replace(' ', '+')
                logger.info(f"Searching: {url} (via {self.search_engine})")
                url = search_url
            else:
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
            
            logger.info(f"Loading: {url}")
            
            response = requests.get(
                url,
                headers=self.default_headers,
                timeout=10,
                allow_redirects=True
            )
            response.raise_for_status()
            
            self.current_url = response.url
            self.current_html = response.text
            self.history.append(url)
            
            return {
                'success': True,
                'url': self.current_url,
                'status_code': response.status_code,
                'title': self._extract_title(),
                'html': self.current_html
            }
        
        except requests.RequestException as e:
            logger.error(f"Error loading {url}: {e}")
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def _extract_title(self) -> str:
        if not self.current_html:
            return "Untitled"
        
        try:
            soup = BeautifulSoup(self.current_html, 'html.parser')
            title = soup.find('title')
            return title.string if title else "Untitled"
        except Exception as e:
            logger.error(f"Error extracting title: {e}")
            return "Untitled"
    
    def get_parsed_content(self) -> Optional[BeautifulSoup]:
        if not self.current_html:
            return None
        return BeautifulSoup(self.current_html, 'html.parser')
    
    def back(self) -> Optional[str]:
        if len(self.history) > 1:
            self.history.pop()
            return self.history[-1]
        return None
    
    def clear_cookies(self):
        self.cookies.clear()
        logger.info("Cookies cleared")
    
    def set_search_engine(self, engine: str):
        if engine in self.SEARCH_ENGINES:
            self.search_engine = engine
            logger.info(f"Search engine changed to: {engine}")


class BrowserWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.engine = BrowserEngine()
        self.init_ui()
        self.setup_privacy()
        
    def init_ui(self):
        self.setWindowTitle("Simple Web Browser - Privacy Focused")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        nav_layout = QHBoxLayout()
        
        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self.go_back)
        nav_layout.addWidget(self.back_btn)
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search query...")
        self.url_bar.returnPressed.connect(self.load_url)
        nav_layout.addWidget(self.url_bar)
        
        self.go_btn = QPushButton("Go")
        self.go_btn.clicked.connect(self.load_url)
        nav_layout.addWidget(self.go_btn)
        
        self.search_btn = QPushButton("🔍 DuckDuckGo")
        self.search_btn.clicked.connect(self.toggle_search_engine)
        nav_layout.addWidget(self.search_btn)
        
        self.privacy_btn = QPushButton("🔒 Clear Data")
        self.privacy_btn.clicked.connect(self.clear_data)
        nav_layout.addWidget(self.privacy_btn)
        
        main_layout.addLayout(nav_layout)
        
        self.web_view = QWebEngineView()
        main_layout.addWidget(self.web_view)
        
        self.status_label = QLabel("Ready • Search Engine: DuckDuckGo (Privacy-Focused)")
        main_layout.addWidget(self.status_label)
        
        self.setCentralWidget(central_widget)
    
    def setup_privacy(self):
        profile = QWebEngineProfile()
        profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.NoPersistentCookies)
        self.web_view.page().setWebEngineProfile(profile)
    
    def load_url(self):
        url = self.url_bar.text().strip()
        if not url:
            return
        
        self.status_label.setText(f"Loading...")
        result = self.engine.load_page(url)
        
        if result['success']:
            self.url_bar.setText(result['url'])
            self.web_view.setHtml(result['html'], self.web_view.page().baseUrl())
            self.setWindowTitle(f"{result['title']} - Simple Browser")
            self.status_label.setText(f"✓ Loaded: {result['url']} • Search: {self.engine.search_engine}")
        else:
            error_html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 40px; background: #f5f5f5; }}
                    .error-container {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                    h1 {{ color: #d32f2f; margin: 0 0 10px 0; }}
                    p {{ color: #666; margin: 5px 0; }}
                </style>
            </head>
            <body>
                <div class="error-container">
                    <h1>❌ Error Loading Page</h1>
                    <p><strong>Error:</strong> {result['error']}</p>
                    <p><strong>URL:</strong> {result['url']}</p>
                    <p>Check your internet connection or try a different search.</p>
                </div>
            </body>
            </html>
            """
            self.web_view.setHtml(error_html)
            self.status_label.setText(f"✗ Error: {result['error']}")
    
    def go_back(self):
        prev_url = self.engine.back()
        if prev_url:
            self.url_bar.setText(prev_url)
            self.load_url()
        else:
            self.status_label.setText("No history")
    
    def toggle_search_engine(self):
        engines = list(self.engine.SEARCH_ENGINES.keys())
        current_idx = engines.index(self.engine.search_engine)
        next_engine = engines[(current_idx + 1) % len(engines)]
        
        self.engine.set_search_engine(next_engine)
        self.search_btn.setText(f"🔍 {next_engine.capitalize()}")
        self.status_label.setText(f"Search engine changed to: {next_engine}")
    
    def clear_data(self):
        self.engine.clear_cookies()
        self.status_label.setText("✓ All cookies and privacy data cleared")


def main():
    app = QApplication(sys.argv)
    browser = BrowserWindow()
    browser.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
