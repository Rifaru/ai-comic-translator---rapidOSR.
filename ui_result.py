# ui_result.py

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PySide6.QtCore import Qt

class ResultWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel("")
        self.label.setWordWrap(True)
        
        # Полупрозрачный фон (190 из 255)
        self.label.setStyleSheet("""
            QLabel {
                background-color: rgba(25, 25, 25, 190);
                color: #F0F0F0;
                border-radius: 8px;
                padding: 10px;
                font-size: 17px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 1px solid rgba(100, 100, 100, 150);
            }
        """)
        self.layout.addWidget(self.label)

    def set_text(self, text: str, bbox: dict = None):
        if bbox:
            # Подстраиваем ширину окна под ширину выделения
            screen_width = QApplication.primaryScreen().geometry().width()
            target_width = max(100, min(bbox["width"], screen_width - 20))
            self.label.setMinimumWidth(target_width)
            self.label.setMaximumWidth(target_width)
        
        self.label.setText(text)
        self.adjustSize()
        
        if bbox:
            self.position_over_bbox(bbox)
        else:
            self.center_on_screen()
        self.show()
        self.activateWindow()
        self.setFocus()

    def position_over_bbox(self, bbox):
        screen = QApplication.primaryScreen().geometry()
        x, y = bbox["left"], bbox["top"]
        # Защита от выхода за границы
        if y + self.height() > screen.height(): y = screen.height() - self.height() - 10
        if x + self.width() > screen.width(): x = screen.width() - self.width() - 10
        self.move(max(10, x), max(10, y))

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: self.hide()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape: self.hide()