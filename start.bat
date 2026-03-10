@echo off
chcp 65001 >nul
title Экранный переводчик (Tesserocr C++ Edition)
echo Инициализация нейросетей...
echo.
echo Убедитесь, что сервер KoboldCPP запущен.
echo (Для закрытия программы нажмите Ctrl+Shift+X)

cd /d "%~dp0"
call venv\Scripts\activate

python main.py
pause