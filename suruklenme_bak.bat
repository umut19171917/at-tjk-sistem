@echo off
REM K80 - uzak-ayak suruklenme olcumu (BEKLEYENLER #9). Cift tikla.
REM OFFLINE + SALT-OKUNUR: hicbir dosyaya yazmaz, canliya dokunmaz.
REM ILK IS: en ustteki "VERI DURUMU" bloguna bak -> 60/90/120/150/180 dk
REM satirlari GORUNUYOR MU? Gorunmuyorsa K76 duzeltmesi islememis demektir.
REM Sonra B tablosunda 6. ayak satirinin n'i >= 15 olunca karar verilebilir.
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
.venv\Scripts\python.exe kod\altili_suruklenme.py
echo.
pause
