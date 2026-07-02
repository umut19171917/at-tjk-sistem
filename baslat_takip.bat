@echo off
REM TJK gunluk otomatik takip - cift tikla baslat (yaris gunu sabahi).
REM PC uyumasin, bu pencere acik kalsin. Kapatinca takip durur.
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo ====================================================
echo  TJK TAKIP baslatiliyor...  (durdurmak icin pencereyi kapat)
echo ====================================================
.venv\Scripts\python.exe kod\takip.py %*
echo.
echo ---- takip bitti / durdu ----
pause
