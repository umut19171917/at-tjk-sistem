@echo off
REM K53 ALTILI canli takip - cift tikla: bekleyen ayaklari sonucla + sayfayi ac.
REM (Gercek bahis DEGIL; +EV yok. Ayri sayfa: raporlar/altili.html)
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo Altili ayak sonuclari isleniyor...
.venv\Scripts\python.exe kod\altili_canli.py --sonucla
echo Kupon ani siralamalari tamamlaniyor (K97; sadece eksikleri doldurur)...
.venv\Scripts\python.exe kod\kupon_ani_geri_kur.py
.venv\Scripts\python.exe kod\altili_canli.py --html
