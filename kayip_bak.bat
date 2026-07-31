@echo off
REM K82 - gunluk hasar raporu: PC kapaliyken ne kaybettik? Cift tikla.
REM OFFLINE + SALT-OKUNUR: hicbir dosyaya yazmaz, canliya dokunmaz.
REM   !! KURULMAYAN ALTILI  -> en pahali (7 kupon + o Altili deneyden duser)
REM   !  GEC KURULDU        -> en sinsi (zamanlama kirlenmesi, BEKLEYENLER #4)
REM   .  DEFTER KAYDI YOK   -> en ucuz (siralama gorunmez + lambda olcumunden duser)
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
.venv\Scripts\python.exe kod\kayip_raporu.py --gun 14
echo.
pause
