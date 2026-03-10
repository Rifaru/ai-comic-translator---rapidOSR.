# screen_capture.py

from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt, QRect, Signal

class SnippingWidget(QWidget):
    # Сигнал передает сразу два bbox: логический и физический
    on_completed = Signal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.start_point = None
        self.end_point = None

    def start_snipping(self):
        self.start_point = None
        self.end_point = None
        geom = QApplication.primaryScreen().virtualGeometry()
        self.setGeometry(geom)
        self.show()
        self.activateWindow()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.globalPosition().toPoint()
            self.end_point = self.start_point
            self.update()

    def mouseMoveEvent(self, event):
        if self.start_point:
            self.end_point = event.globalPosition().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.start_point:
            self.end_point = event.globalPosition().toPoint()
            rect = QRect(self.start_point, self.end_point).normalized()

            if rect.width() > 5 and rect.height() > 5:
                ratio = self.screen().devicePixelRatio()
                
                # Координаты для интерфейса (логические)
                logical = {"top": rect.top(), "left": rect.left(), "width": rect.width(), "height": rect.height()}
                # Координаты для скриншота (физические)
                physical = {
                    "top": int(rect.top() * ratio),
                    "left": int(rect.left() * ratio),
                    "width": int(rect.width() * ratio),
                    "height": int(rect.height() * ratio)
                }
                self.on_completed.emit({"logical": logical, "physical": physical})
            else:
                self.hide()
            self.start_point = None
            self.end_point = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        if self.start_point and self.end_point:
            global_rect = QRect(self.start_point, self.end_point).normalized()
            local_rect = QRect(self.mapFromGlobal(global_rect.topLeft()), self.mapFromGlobal(global_rect.bottomRight()))
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(local_rect, Qt.GlobalColor.transparent)
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            painter.setPen(QPen(QColor(255, 60, 60), 2))
            painter.drawRect(local_rect)