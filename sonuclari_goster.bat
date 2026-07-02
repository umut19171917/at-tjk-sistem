@echo off
REM Sonuclari cek + okunur HTML tabloyu tarayicida ac (PowerShell yazmadan).
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo Sonuclar cekiliyor ve tablo hazirlaniyor...
.venv\Scripts\python.exe kod\defter.py sonucla
.venv\Scripts\python.exe kod\defter.py html
