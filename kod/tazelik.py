# -*- coding: utf-8 -*-
"""
tazelik.py — K110: TURETILMIS VERI BAYATLIK UYARISI.

NEDEN VAR: 19 Agu 2026 kod incelemesinde bulundu ki offline analiz yigini SESSIZCE
bayatlamis -- ozellikli.csv 41 gun, altili_tam/altili_olasilik 30 gun, olasilik_bot1
20 gun eskiydi. Somut sonuc: Agustos'ta oynanan 272 ayak kosusunun SIFIRI olasilik
dosyalarinda yoktu, yani o gun calistirilan her backtest Temmuz dunyasinda kosuyordu
ve bunu soyleyen hicbir sey yoktu.

gunluk.hesapla K36'dan beri katilim.csv icin bayatlik uyariyor; TURETILMIS dosyalar icin
ayni koruma yoktu. Bu modul o boslugu doldurur.

TASARIM KURALI: bu modulu CANLI YOL ASLA import etmez. Offline betikler yalnizca
main() ICINDE import eder -- boylece import zinciri canliya hic dokunmaz ve buradaki
bir hata kupon kurmayi engelleyemez.

Kullanim (offline betigin main()'inin BASINDA):
    from tazelik import uyar
    uyar("altili_tam.csv", "altili_olasilik.csv")
"""
from datetime import datetime
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
ESIK_GUN = 7          # bu kadar gun eskiyse uyar

# turetilmis dosya -> onu ureten komut (uyarida gosterilir)
URETICI = {
    "ozellikli.csv":            "python kod/ozellik.py",
    "altili_olasilik.csv":      "python kod/altili_olasilik.py",
    "altili_olasilik_bot1.csv": "python kod/altili_bot1_test.py --yenile",
    "altili_tam.csv":           "python kod/altili_tam.py",
    "nli_ganyan.csv":           "python kod/nli_ayikla.py",
    "katilim.csv":              "python kod/guncelle.py",
}


def _yas_gun(p):
    try:
        return (datetime.now() - datetime.fromtimestamp(p.stat().st_mtime)).days
    except OSError:
        return None


def uyar(*dosyalar, esik=ESIK_GUN, sessiz_taze=True):
    """Verilen turetilmis dosyalarin yasini basar; esikten eskiyse GORUNUR uyari verir.
    Hicbir sey firlatmaz, hicbir seyi engellemez -- yalnizca soyler.
    Doner: bayat dosya adlarinin listesi (bos = hepsi taze)."""
    if not dosyalar:
        dosyalar = tuple(URETICI)
    bayat, satir = [], []
    for ad in dosyalar:
        p = KOK / "veri" / ad
        if not p.exists():
            satir.append(f"    {ad:<26} YOK          -> {URETICI.get(ad, '?')}")
            bayat.append(ad)
            continue
        y = _yas_gun(p)
        if y is None:
            continue
        if y >= esik:
            satir.append(f"    {ad:<26} {y:>3} gun eski -> {URETICI.get(ad, '?')}")
            bayat.append(ad)
        elif not sessiz_taze:
            satir.append(f"    {ad:<26} {y:>3} gun (taze)")
    if bayat:
        print("=" * 96)
        print(f"!!! BAYAT TURETILMIS VERI ({esik} gun esigi) — bu backtest'in sayilari GUNCEL DEGIL")
        print("=" * 96)
        print("\n".join(satir))
        print("    Tazelemek icin yukaridaki komutlari SIRAYLA calistir")
        print("    (ozellik -> altili_olasilik / altili_bot1_test --yenile -> altili_tam).")
        print("    UYARI: takip.py kosarken ozellik.py calistirma (katilim.csv yazma cakismasi).")
        print("=" * 96)
    elif not sessiz_taze:
        print("tazelik: turetilmis veri guncel.\n" + "\n".join(satir))
    return bayat


if __name__ == "__main__":
    print("TURETILMIS VERI YASI (hepsi):")
    uyar(sessiz_taze=False)
