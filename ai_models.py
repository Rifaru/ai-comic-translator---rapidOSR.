# ai_models.py

import re
import requests
import config
from PIL import Image
import tesserocr

print("Инициализация Tesserocr (C++ API)...")

def run_ocr(img_rgb_array) -> str:
    """Распознавание текста через сверхбыстрый Tesserocr (C++ API)."""
    # Конвертируем массив OpenCV (numpy) в картинку PIL для Tesserocr
    pil_image = Image.fromarray(img_rgb_array)
    
    try:
        # Указываем путь к папке tessdata (которая лежит в папке проекта)
        # PSM.SINGLE_BLOCK (6) идеально подходит для абзацев комиксов
        with tesserocr.PyTessBaseAPI(path='./tessdata', lang='eng', psm=tesserocr.PSM.SINGLE_BLOCK) as api:
            api.SetImage(pil_image)
            text = api.GetUTF8Text()
            
            if text and text.strip():
                # Tesseract оставляет \n, склеиваем их в одно красивое предложение
                full_text = " ".join(text.split()).strip()
                print(f"--- TESSERACT ПРОЧИТАЛ:\n{full_text}")
                return full_text
    except Exception as e:
        print(f"Ошибка OCR: {e}")
        return ""
    
    return ""

def clean_response(text: str) -> str:
    """Убирает <think> теги и мусор."""
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'</?think>', '', text)
    text = re.sub(r'^assistant\s*', '', text, flags=re.IGNORECASE)
    return text.strip()

def translate_text(text: str) -> str:
    """Запрос к KoboldCPP."""
    payload = {
        "messages":[
            {"role": "system", "content": config.SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ],
        "temperature": getattr(config, 'TEMPERATURE', 0.2),
        "max_tokens": getattr(config, 'MAX_TOKENS', 1024)
    }

    if hasattr(config, 'TOP_P'): payload["top_p"] = config.TOP_P
    if hasattr(config, 'TOP_K'): payload["top_k"] = config.TOP_K
    if hasattr(config, 'FREQUENCY_PENALTY'): payload["frequency_penalty"] = config.FREQUENCY_PENALTY

    try:
        response = requests.post(config.KOBOLD_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        raw = data["choices"][0]["message"]["content"].strip()
        return clean_response(raw)

    except requests.exceptions.Timeout:
        return "❌ Ошибка: Модель не ответила за 120 секунд"
    except requests.exceptions.ConnectionError:
        return "❌ Ошибка: KoboldCPP не запущен"
    except Exception as e:
        return f"❌ Ошибка связи с ИИ: {str(e)}"