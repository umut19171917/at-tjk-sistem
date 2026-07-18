"""
veri_commit.py — K50: deney verisinin HAFTALIK otomatik git commit'i.
Neden: defter.csv + paper_kupon.csv deneyin ham verisi; commit'lenmedikce tek kopya diskte
(zip yedek manuel ve seyrek). Haftalik commit = haftada bir geri-donus noktasi; bozulma
(script hatasi / Excel kazasi / disk) en fazla 1 haftalik veriyi riske atar.
"TJK Veri Commit" gorevi pazartesi 22:45'te calistirir; elle de calisir. Degisiklik yoksa
sessizce cikar (idempotent).
"""
import shutil
import subprocess
from datetime import date
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
GIT = shutil.which("git") or r"C:\Program Files\Git\cmd\git.exe"


def calistir(*args):
    return subprocess.run([GIT, *args], cwd=KOK, capture_output=True, text=True,
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def main():
    yollar = ["veri/defter.csv", "veri/paper_kupon.csv",
              "raporlar/gunluk", "raporlar/defter.html", "raporlar/paper.html"]
    if (KOK / "veri" / "bahisler.csv").exists():      # K37 yeniden aktiflesirse o da
        yollar.append("veri/bahisler.csv")
    r = calistir("add", "--", *yollar)
    if r.returncode != 0:
        print(f"git add hata: {r.stderr.strip()}")
        return 1
    if calistir("diff", "--cached", "--quiet").returncode == 0:
        print("veri degisikligi yok; commit gerekmiyor.")
        return 0
    r = calistir("commit", "-m", f"veri: deney kaydi {date.today().isoformat()} (otomatik, K50)")
    print(r.stdout.strip() or r.stderr.strip())
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
