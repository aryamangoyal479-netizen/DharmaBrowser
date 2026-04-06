import sys
import ctypes
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import *

try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('dharma.browser.v1')
except:
    pass

class DharmaBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setWindowIcon(QIcon("icon.ico"))
        
        self.setStyleSheet("""
            QMainWindow { background-color: #000; border: 1px solid #333; }
            #TopBar { background-color: #000; }
            
            /* Tight Tab Styling */
            QTabBar::tab { 
                background: #1a1a1a; color: #888; padding: 6px 15px; 
                margin-top: 4px; margin-right: 2px; min-width: 120px; 
                border-top-left-radius: 8px; border-top-right-radius: 8px;
            }
            QTabBar::tab:selected { background: #333; color: white; }
            QTabWidget::pane { border: none; }

            /* Nav Bar right under tabs */
            QToolBar { background-color: #333; border: none; padding: 4px; spacing: 10px; }
            QLineEdit { background-color: #1a1a1a; color: white; border-radius: 12px; padding: 5px; border: 1px solid #444; }
            
            /* Small Window Buttons */
            QPushButton.WinBtn { background: transparent; color: white; width: 45px; height: 35px; border: none; font-size: 14px; }
            QPushButton.WinBtn:hover { background-color: #333; }
            #CloseBtn:hover { background-color: #e81123; }
        """)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # --- ROW 1: TABS + CONTROLS (STRICT HEIGHT) ---
        self.top_bar = QWidget()
        self.top_bar.setObjectName("TopBar")
        self.top_bar.setFixedHeight(40) # LOCK HEIGHT TO 40PX
        self.top_bar.installEventFilter(self) 
        
        self.top_layout = QHBoxLayout(self.top_bar)
        self.top_layout.setContentsMargins(0, 0, 0, 0)
        self.top_layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.top_layout.addWidget(self.tabs)

        # Spacer to keep buttons on the far right
        self.top_layout.addStretch()

        # Window Controls
        self.btn_min = QPushButton("–"); self.btn_min.setProperty("class", "WinBtn")
        self.btn_max = QPushButton("▢"); self.btn_max.setProperty("class", "WinBtn")
        self.btn_close = QPushButton("✕"); self.btn_close.setProperty("class", "WinBtn"); self.btn_close.setObjectName("CloseBtn")
        
        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_max.clicked.connect(self.toggle_maximize)
        self.btn_close.clicked.connect(self.close)

        self.top_layout.addWidget(self.btn_min)
        self.top_layout.addWidget(self.btn_max)
        self.top_layout.addWidget(self.btn_close)

        # --- ROW 2: NAV BAR ---
        self.nav_bar = QToolBar()
        self.nav_bar.setMovable(False)
        self.add_nav_btn("‹", lambda: self.current_browser().back())
        self.add_nav_btn("›", lambda: self.current_browser().forward())
        self.add_nav_btn("↻", lambda: self.current_browser().reload())
        self.add_nav_btn("+", self.add_new_tab)
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.nav_bar.addWidget(self.url_bar)

        # --- ROW 3: CONTENT ---
        self.content_stack = QStackedWidget()

        self.main_layout.addWidget(self.top_bar)
        self.main_layout.addWidget(self.nav_bar)
        self.main_layout.addWidget(self.content_stack)

        self.add_new_tab(QUrl('https://google.com'), 'Home')
        self.tabs.currentChanged.connect(self.switch_tab)
        self.resize(1100, 700)

    def eventFilter(self, obj, event):
        if obj == self.top_bar and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self.windowHandle().startSystemMove()
                return True
        return super().eventFilter(obj, event)

    def add_new_tab(self, qurl=None, label="New Tab"):
        if not qurl: qurl = QUrl('https://google.com')
        browser = QWebEngineView()
        browser.setUrl(qurl)
        self.content_stack.addWidget(browser)
        i = self.tabs.addTab(QWidget(), label) 
        self.tabs.setCurrentIndex(i)
        browser.loadFinished.connect(lambda: self.update_tab_title(browser))
        browser.urlChanged.connect(lambda q: self.update_url_bar(q, browser))

    def switch_tab(self, i):
        self.content_stack.setCurrentIndex(i)
        if self.current_browser(): self.url_bar.setText(self.current_browser().url().toString())

    def update_tab_title(self, browser):
        idx = self.content_stack.indexOf(browser)
        if idx != -1: self.tabs.setTabText(idx, browser.page().title()[:12])

    def update_url_bar(self, q, browser):
        if browser == self.current_browser(): self.url_bar.setText(q.toString())

    def close_tab(self, i):
        if self.tabs.count() > 1:
            self.tabs.removeTab(i)
            self.content_stack.removeWidget(self.content_stack.widget(i))
        else: self.close()

    def current_browser(self): return self.content_stack.currentWidget()

    def navigate_to_url(self):
        u = self.url_bar.text()
        if "." not in u: u = f"https://google.com{u}"
        elif "http" not in u: u = f"https://{u}"
        self.current_browser().setUrl(QUrl(u))

    def toggle_maximize(self):
        if self.isMaximized(): self.showNormal()
        else: self.showMaximized()

    def add_nav_btn(self, txt, slot):
        a = QAction(txt, self); a.triggered.connect(slot); self.nav_bar.addAction(a)

app = QApplication(sys.argv)
win = DharmaBrowser()
win.show()
sys.exit(app.exec())
