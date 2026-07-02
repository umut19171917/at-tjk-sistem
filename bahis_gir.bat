@echo off
REM GERCEK kupon kaydi (K37) - cift tikla, sorulara cevap ver.
REM Kupon basina bir kayit. Ganyan tek-at kuponu sonuclarla otomatik kapanir;
REM diger turlerin odemesini sonuc_gir ile isle (defter.py bahis-sonuc).
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo ==== GERCEK BAHIS KAYDI ====
set /p pist=Pist (or. ANKARA):
set /p kosu=Kosu no (altili vb. icin ILK ayak):
set /p tur=Tur (ganyan/plase/ikili/uclu/altili/...):
set /p secim=Secim (at no; kombine serbest metin, or. 3-7):
set /p miktar=Kupon tutari TL:
.venv\Scripts\python.exe kod\defter.py bahis --pist "%pist%" --kosu "%kosu%" --tur "%tur%" --secim "%secim%" --miktar %miktar%
echo.
pause
