@echo off
REM K49: takip artik OTOMATIK (gorev her 15 dk'da bir gecis yapar; elle baslatma GEREKMEZ).
REM Bu dosya = ELLE TEK GECIS: simdi vadesi gelen kosulari isler, durumu gosterir, cikar.
REM (Gorev calismiyorsa/bekci uyardiysa kurtarma icin cift tikla.)
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
echo ==== TJK ELLE GECIS (K49) ====
.venv\Scripts\python.exe kod\takip.py %*
echo.
echo ---- gecis bitti (otomatik gorev 15 dk'da bir zaten calisiyor) ----
pause
