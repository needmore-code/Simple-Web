import sys
from PyQt5.QtCore import QUrl, QSize
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction, QLineEdit,
    QTabWidget, QWidget, QVBoxLayout, QStatusBar, QLabel, QInputDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView


def format_url(text: str) -> QUrl:
    text = text.strip()
    if not text:
        return QUrl("about:blank")
    if "://" not in text:
        text = "http://" + text
    return QUrl(text)


class BrowserTab(QWidget):
    def __init__(self, url: QUrl = QUrl("https://www.google.com"), parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.view = QWebEngineView(self)
        self.view.setUrl(url)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.view)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyChromium Browser")
        self.resize(1200, 800)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_current_tab_changed)
        self.setCentralWidget(self.tabs)

        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(16, 16))
        self.addToolBar(navtb)

        back_btn = QAction("←", self)
        back_btn.setStatusTip("Back")
        back_btn.triggered.connect(self.go_back)
        navtb.addAction(back_btn)

        forward_btn = QAction("→", self)
        forward_btn.setStatusTip("Forward")
        forward_btn.triggered.connect(self.go_forward)
        navtb.addAction(forward_btn)

        reload_btn = QAction("⟳", self)
        reload_btn.setStatusTip("Reload")
        reload_btn.triggered.connect(self.reload_page)
        navtb.addAction(reload_btn)

        home_btn = QAction("🏠", self)
        home_btn.setStatusTip("Home")
        home_btn.triggered.connect(self.go_home)
        navtb.addAction(home_btn)

        navtb.addSeparator()

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        navtb.addSeparator()

        new_tab_btn = QAction("+", self)
        new_tab_btn.setStatusTip("Open new tab")
        new_tab_btn.triggered.connect(self.add_tab_prompt)
        navtb.addAction(new_tab_btn)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.progress_label = QLabel("")
        self.status.addPermanentWidget(self.progress_label)

        self.add_tab(QUrl("https://www.google.com"), "New Tab")

    def add_tab(self, qurl: QUrl = QUrl("about:blank"), label: str = "New Tab"):
        new_tab = BrowserTab(qurl)
        index = self.tabs.addTab(new_tab, label)
        self.tabs.setCurrentIndex(index)

        webview = new_tab.view
        webview.urlChanged.connect(lambda url, w=webview: self.update_urlbar(url, w))
        webview.loadStarted.connect(lambda w=webview: self.on_load_started(w))
        webview.loadProgress.connect(lambda p, w=webview: self.on_load_progress(p, w))
        webview.loadFinished.connect(lambda ok, w=webview: self.on_load_finished(ok, w))
        webview.titleChanged.connect(lambda title, t=new_tab: self.tabs.setTabText(self.tabs.indexOf(t), title))

    def add_tab_prompt(self):
        text, ok = QInputDialog.getText(self, "Open URL", "URL or search:")
        if ok:
            if text.strip():
                self.add_tab(format_url(text.strip()), text.strip())
            else:
                self.add_tab(QUrl("about:blank"), "New Tab")
        else:
            self.add_tab(QUrl("about:blank"), "New Tab")

    def close_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def current_webview(self) -> QWebEngineView:
        widget = self.tabs.currentWidget()
        if widget:
            return widget.view
        return None

    def go_back(self):
        w = self.current_webview()
        if w:
            w.back()

    def go_forward(self):
        w = self.current_webview()
        if w:
            w.forward()

    def reload_page(self):
        w = self.current_webview()
        if w:
            w.reload()

    def go_home(self):
        w = self.current_webview()
        if w:
            w.setUrl(QUrl("https://www.google.com"))

    def navigate_to_url(self):
        text = self.urlbar.text()
        url = format_url(text)
        w = self.current_webview()
        if w:
            w.setUrl(url)

    def update_urlbar(self, q: QUrl, browser: QWebEngineView):
        if browser != self.current_webview():
            return
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def on_current_tab_changed(self, i):
        w = self.current_webview()
        if w:
            self.update_urlbar(w.url(), w)

    def on_load_started(self, webview):
        if webview == self.current_webview():
            self.progress_label.setText("Loading...")

    def on_load_progress(self, progress, webview):
        if webview == self.current_webview():
            self.progress_label.setText(f"{progress}%")

    def on_load_finished(self, ok, webview):
        if webview == self.current_webview():
            if ok:
                self.progress_label.setText("")
            else:
                self.progress_label.setText("Failed to load page")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PyChromium Browser")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()