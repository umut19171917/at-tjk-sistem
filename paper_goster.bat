@echo off
REM K42 PAPER TEST sonuclari - cift tikla: acik kuponlari kapat + ayri sayfayi ac.
REM (Gercek para DEGIL; defter.html'den ayri sayfa: raporlar/paper.html)
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo Paper kuponlar sonuclaniyor...
.venv\Scripts\python.exe kod\paper.py sonucla
.venv\Scripts\python.exe kod\paper.py html
