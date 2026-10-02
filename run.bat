@echo off
title SmartDrop - Akilli Dosya Duzenleyici
echo SmartDrop baslatiliyor...
python app.py
if %errorlevel% neq 0 (
    echo [HATA] Uygulama calisirken bir hata olustu.
    pause
)
