@echo off
title SmartDrop Setup (Windows)
echo ==============================================
echo       SmartDrop Desktop Setup
echo ==============================================
echo Python ortamı kontrol ediliyor...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [HATA] Python bulunamadi! Lutfen Python 3.12+ yukleyin ve PATH'e ekleyin.
    pause
    exit /b 1
)

echo Gerekli paketler yukleniyor (PySide6, pytest)...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [UYARI] Bazi paketler yuklenememis olabilir.
) else (
    echo Kurulum basariyla tamamlandi!
)
echo.
echo smartdrop baslatmak icin run.bat dosyasini calistirabilirsiniz.
pause
