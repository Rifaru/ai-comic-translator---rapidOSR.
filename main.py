# main.py

import sys, time, threading, keyboard, cv2, mss
import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, QThread
from config import HOTKEY_TRANSLATE, HOTKEY_QUIT
from screen_capture import SnippingWidget
from ui_result import ResultWindow
from ai_models import run_ocr, translate_text

class AppSignals(QObject):
    translate_hotkey = Signal()
    quit_hotkey = Signal()

class TranslationWorker(QThread):
    finished = Signal(str)
    def __init__(self, img_rgb):
        super().__init__()
        self.img_rgb = img_rgb

    def run(self):
        try:
            text = run_ocr(self.img_rgb)
            if not text.strip():
                self.finished.emit("❌ Текст не найден.")
                return
            translated = translate_text(text)
            self.finished.emit(translated)
        except Exception as e:
            self.finished.emit(f"❌ Ошибка: {str(e)}")

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        self.signals = AppSignals()
        self.snipping_widget = SnippingWidget()
        self.result_window = ResultWindow()
        self.signals.translate_hotkey.connect(self.snipping_widget.start_snipping)
        self.signals.quit_hotkey.connect(self.quit_app)
        self.snipping_widget.on_completed.connect(self.on_snipping_completed)
        threading.Thread(target=self.listen_hotkeys, daemon=True).start()

    def listen_hotkeys(self):
        keyboard.add_hotkey(HOTKEY_TRANSLATE, lambda: self.signals.translate_hotkey.emit())
        keyboard.add_hotkey(HOTKEY_QUIT, lambda: self.signals.quit_hotkey.emit())
        keyboard.wait()

    def on_snipping_completed(self, bboxes):
        self.snipping_widget.hide()
        self.app.processEvents()
        time.sleep(0.06)

        # 1. Скриншот
        with mss.mss() as sct:
            img_bgra = np.array(sct.grab(bboxes["physical"]))
            
        # ==========================================
        # 2. МЯГКИЙ COMPUTER VISION (Сохраняем детали)
        # ==========================================
        # 1. Переводим в ЧБ
        gray = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA2GRAY)
        
        # 2. CLAHE (Мягкое выравнивание контраста)
        # Это поможет буквам выделиться на фоне свитка, не превращая их в "рваные" линии
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # 3. LANCZOS4 Upscaling (Увеличение в 2.5 раза)
        # Это гораздо точнее сохраняет форму рукописных букв, чем CUBIC
        img_processed = cv2.resize(enhanced, None, fx=2.5, fy=2.5, interpolation=cv2.INTER_LANCZOS4)
        
        # 4. Возвращаем в RGB для Tesserocr (Бинаризацию НЕ ДЕЛАЕМ!)
        img_rgb = cv2.cvtColor(img_processed, cv2.COLOR_GRAY2RGB)
        # ==========================================

        self.current_bbox = bboxes["logical"]
        self.result_window.set_text("⏳ Читаю текст...", self.current_bbox)
        
        self.worker = TranslationWorker(img_rgb)
        self.worker.finished.connect(self.on_translation_finished)
        self.worker.start()

    def on_translation_finished(self, text):
        clean_text = text.strip('«»"\'')
        self.result_window.set_text(clean_text, self.current_bbox)
        
        # Сохранение в лог (по желанию)
        try:
            with open("history.txt", "a", encoding="utf-8") as f:
                f.write(f"{clean_text}\n\n")
        except: pass

    def quit_app(self):
        self.app.quit()

    def run(self):
        print("🚀 Переводчик (Tesserocr Edition) запущен!")
        sys.exit(self.app.exec())

if __name__ == "__main__":
    controller = AppController()
    controller.run()