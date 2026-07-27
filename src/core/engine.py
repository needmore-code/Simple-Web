"""Browser engine - handles page loading and rendering"""

import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class BrowserEngine:
    """Core browser engine for fetching and parsing web pages"""
    
    def __init__(self):
        self.current_url: Optional[str] = None
        self.current_html: Optional[str] = None
        self.history = []
        self.cookies = {}  # Privacy: minimal cookie storage
        
        # Privacy-focused headers
        self.default_headers = {
            'User-Agent': 'SimpleBrowser/1.0 (Privacy-Focused)',
            'DNT': '1',  # Do Not Track
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
        }
    
    def load_page(self, url: str) -> Dict:
        """Fetch and parse a web page"""
        try:
            # Ensure valid URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            logger.info(f"Loading: {url}")
            
            # Privacy: Don't send referrer, minimal headers
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
        """Extract page title from HTML"""
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
        """Get parsed HTML content"""
        if not self.current_html:
            return None
        return BeautifulSoup(self.current_html, 'html.parser')
    
    def back(self) -> Optional[str]:
        """Navigate back in history"""
        if len(self.history) > 1:
            self.history.pop()
            return self.history[-1]
        return None
    
    def clear_cookies(self):
        """Privacy: Clear all cookies"""
        self.cookies.clear()
        logger.info("Cookies cleared")
