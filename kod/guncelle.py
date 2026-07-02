"""
guncelle.py — arsivi bugune getir (K36 veri-tazeleme protokolu).
  1) kazi.py --guncelle : arsivdeki son gunden bugune yeni ham JSON indirir
     (sinir gunu yeniden indirilir; gun-ici kismi inmis olabilir).
  2) yeni ham dosya indiyse (veya katilim.csv ham'dan eskiyse) duzlestir.py ile
     katilim.csv yeniden uretilir; yoksa atlanir (sabah hizli acilis).

NEDEN: katilim.csv donuk kalirsa atlarin son kosulari form/kariyer ozelliklerine girmez
(sessiz bayatlama). gunluk.hesapla bayatlik uyarisi verir ama duzeltme BU script.

DIKKAT: takip.py CALISIRKEN calistirma — takip her kosuda katilim.csv okur; yazma
aninda okuma yarim dosya gorur. baslat_takip.bat bunu dogru sirayla (once guncelle,
sonra takip) zaten yapar.

Kullanim:  python kod/guncelle.py     (veya baslat_takip.bat icinden otomatik)
"""
import subprocess
import sys
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
HAM = KOK / "veri" / "ham"
KATILIM = KOK / "veri" / "katilim.csv"


def son_ham_mtime():
    dosyalar = list((HAM / "sonuclar").glob("*.json")) + list((HAM / "program").glob("*.json"))
    return max((f.stat().st_mtime for f in dosyalar), default=0.0)


def main():
    r = subprocess.run([sys.executable, str(KOK / "kod" / "kazi.py"), "--guncelle"])
    if r.returncode != 0:
        print("UYARI: kazima hata verdi; eldeki arsivle devam edilecek (bayatlik uyarisina bak).")
    if son_ham_mtime() > (KATILIM.stat().st_mtime if KATILIM.exists() else 0.0):
        print("yeni ham veri var -> duzlestir calisiyor (birkac dakika surebilir)...")
        r2 = subprocess.run([sys.executable, str(KOK / "kod" / "duzlestir.py")])
        if r2.returncode != 0:
            print("HATA: duzlestir basarisiz; katilim.csv YENILENMEDI. Elle: python kod/duzlestir.py")
            sys.exit(1)
        print("arsiv guncellendi.")
    else:
        print("arsiv zaten guncel; duzlestir gerekmiyor.")


if __name__ == "__main__":
    main()
