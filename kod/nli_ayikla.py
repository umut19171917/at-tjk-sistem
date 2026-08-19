# -*- coding: utf-8 -*-
"""
nli_ayikla.py — N'LI GANYAN olay tablosu: veri/nli_ganyan.csv (K110'da YAZILDI).

NEDEN SONRADAN YAZILDI: bu dosyayi K94 uretmisti ama URETICI BETIK KAYDEDILMEMISTI
(gecici bir betikle uretilip atilmis). 19 Agu 2026 kod incelemesinde fark edildi:
veri/nli_ganyan.csv'yi OKUYAN var (nli_backtest.py), YAZAN yoktu -> dosya ne
tazelenebiliyor ne de yeniden uretilebiliyordu. K108'in (4'lu/5'li kolunun reddi)
TAMAMI bu dosyaya dayaniyor; uretici olmadan o karar dogrulanamaz durumdaydi.

NE YAPAR: ham sonuc kartlarindaki BAHISLER_TR metninden 3/4/5/6/7'li GANYAN
olaylarini cikarir. Her olay icin: kazanan kombo, temettu (veya devir), ve kombonun
GERCEK KAZANANLARLA eslestirilmesiyle bulunan AYAK KOSU KODLARI.

YAPI (K94'te cozuldu, burada aynen korunuyor):
  - Temettu, bahsin BITTIGI kosuya ilisir; ayaklar o kosuda biten N ARDISIK kosudur.
  - Alt kademeler ust kademenin SONDAN kesilmis alt kumesidir
    (6'LI(a/b/c/d/e/f) -> 5'LI(b/c/d/e/f) -> 4'LU(c/d/e/f) -> 3'LU(d/e/f)).
  - Ayni olay birden fazla kosunun BAHISLER_TR'sinde YANKILANABILIR -> tekillestirilir.
  - "N." oneki TUTARSIZ (bazen yok) -> pencere metinden DEGIL, komboyu gercek
    kazananlarla esleyerek bulunur (altili_tam.py / egzotik6_ayikla.py ile ayni teknik).

DIKKAT: PLASE haric. "7'LI PLASE(...)" ayri bir bahistir, ganyan degildir.

Kullanim:  python kod/nli_ayikla.py            (tam yeniden uretim)
           python kod/nli_ayikla.py --dogrula  (mevcut dosyayla karsilastir, YAZMAZ)
YEREL, TOKEN=0.
"""
import json
import re
import sys
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parent.parent
HAM = KOK / "veri" / "ham" / "sonuclar"
CIKTI = KOK / "veri" / "nli_ganyan.csv"
KOL = ["tarih", "sehir", "urun", "seq", "tip", "race_kodlar", "kombo", "tl", "beraberlik"]

# 3..7'li GANYAN. Turkce ekler degisken (LI / L-noktasiz-I / LU / L-umlaut-U).
# PLASE ELENIR (ayri bahis). Iki odeme bicimi:
#   "1.234,50TL"   |   "Bilen yok, 1.234,50 TL devreder."
PAT = re.compile(
    r"(?:(\d+)\.\s*)?"                       # 1: opsiyonel sira oneki ("2. ")
    r"([34567])'(?:LI|Lİ|LU|LÜ)\s*GANYAN"
    r"\(([\d/,]+)\)\s*:\s*"                  # 3: kombo
    r"(?:Bilen[^,]*,\s*([\d.,]+)\s*TL\s*dev\S*|([\d.,]+)\s*TL)",   # 4: devir  5: odendi
    re.IGNORECASE)


def vfloat(s):
    """TR sayi: '1.234,50' -> 1234.5 ; '135,20' -> 135.2"""
    if s is None:
        return None
    s = s.strip()
    s = s.replace(".", "").replace(",", ".") if ("," in s and "." in s) else s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def kart_oku(f):
    """Sonuc JSON -> [(kosu_no, KOD, kazananlar, bahis_metni)] kosu SIRASINA gore."""
    o = json.load(open(f, encoding="utf-8"))
    kos = []
    for k in o.get("kosular", []):
        try:
            no = int(k.get("RACENO") or k.get("NO"))
        except (TypeError, ValueError):
            continue
        ws = set()
        for a in k.get("atlar", []):
            try:
                if int(a.get("SONUC")) == 1:
                    ws.add(int(a.get("NO")))
            except (TypeError, ValueError):
                pass
        kos.append((no, k.get("KOD"), ws, k.get("BAHISLER_TR") or ""))
    kos.sort(key=lambda x: x[0])
    return kos


def pencere_bul(kombo, kazananlar, n):
    """Komboyu gercek kazananlarla esleyerek N-ardisik kosu ofsetini bul (yoksa None).
    altili_tam.pencere_bul'un N-ayak hali; ayni teknik."""
    ayaklar = [set(int(x) for x in p.split(",") if x.strip().isdigit())
               for p in kombo.split("/")]
    if len(ayaklar) != n:
        return None
    for off in range(0, len(kazananlar) - n + 1):
        if all(kazananlar[off + i] & ayaklar[i] for i in range(n)):
            return off
    return None


def uret():
    dosyalar = sorted(HAM.glob("*.json"))
    print(f"ham sonuc karti: {len(dosyalar):,}")
    satir, eslesmeyen = [], 0
    for f in dosyalar:
        ad = f.stem                                   # 20260818_KOCAELI
        if "_" not in ad:
            continue
        ymd, sehir = ad.split("_", 1)
        if len(ymd) != 8 or not ymd.isdigit():
            continue
        tarih = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}"
        try:
            kos = kart_oku(f)
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            continue
        if len(kos) < 3:
            continue
        kodlar = [k[1] for k in kos]
        kazananlar = [k[2] for k in kos]
        tam_metin = " ".join(k[3] for k in kos)       # yanki -> asagida tekillestirilir

        gorulen, sayac = set(), {}
        for m in PAT.finditer(tam_metin):
            onek, urun, kombo, dev, odn = m.groups()
            urun = int(urun)
            if (urun, kombo) in gorulen:               # ayni olayin yankisi
                continue
            gorulen.add((urun, kombo))
            off = pencere_bul(kombo, kazananlar, urun)
            sayac[urun] = sayac.get(urun, 0) + 1
            seq = int(onek) if onek else sayac[urun]
            if off is None:
                eslesmeyen += 1
                rk, ber = "", ""
            else:
                rk = "/".join(str(x) for x in kodlar[off:off + urun])
                ber = int(any(len(kazananlar[off + i]) > 1 for i in range(urun)))
            satir.append({
                "tarih": tarih, "sehir": sehir, "urun": urun, "seq": seq,
                "tip": "devir" if dev else "odendi",
                "race_kodlar": rk, "kombo": kombo,
                "tl": vfloat(dev or odn), "beraberlik": ber,
            })
    df = pd.DataFrame(satir, columns=KOL)
    df = df.drop_duplicates(subset=["tarih", "sehir", "urun", "kombo"], keep="first")
    df = df.sort_values(["tarih", "sehir", "urun", "seq"]).reset_index(drop=True)
    print(f"olay: {len(df):,} | ayak eslestirilemeyen: {eslesmeyen}")
    print(df.groupby("urun").size().to_string())
    return df


def dogrula(yeni):
    """Mevcut nli_ganyan.csv'yi yeniden uretebiliyor muyuz? (uretici DOGRULUGUNUN ISPATI)"""
    if not CIKTI.exists():
        print("mevcut dosya yok, karsilastirma atlandi.")
        return
    e = pd.read_csv(CIKTI, low_memory=False)
    e = e[e["tarih"] <= yeni["tarih"].max()]
    a = ["tarih", "sehir", "urun", "kombo"]
    m = e.merge(yeni, on=a, how="outer", indicator=True, suffixes=("_eski", "_yeni"))
    print("\n" + "=" * 84)
    print("DOGRULAMA — mevcut (K94) dosyayla karsilastirma")
    print("=" * 84)
    print(f"  ortak olay        : {int((m['_merge'] == 'both').sum()):,}")
    print(f"  yalniz ESKIDE     : {int((m['_merge'] == 'left_only').sum()):,}")
    print(f"  yalniz YENIDE     : {int((m['_merge'] == 'right_only').sum()):,}  (yeni gunler dahil)")
    o = m[m["_merge"] == "both"]
    if len(o):
        tl_f = (pd.to_numeric(o["tl_eski"], errors="coerce")
                - pd.to_numeric(o["tl_yeni"], errors="coerce")).abs()
        print(f"  temettu farki     : max={tl_f.max():.4f}  ayni olan: "
              f"{int((tl_f < 0.01).sum()):,}/{len(o):,}")
        rk_ayni = int((o["race_kodlar_eski"].astype(str)
                       == o["race_kodlar_yeni"].astype(str)).sum())
        print(f"  ayak kodlari ayni : {rk_ayni:,}/{len(o):,} "
              f"(%{100*rk_ayni/max(len(o),1):.1f})")


def main():
    yeni = uret()
    dogrula(yeni)
    if "--dogrula" in sys.argv:
        print("\n--dogrula: dosya YAZILMADI.")
        return
    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    yeni.to_csv(CIKTI, index=False, encoding="utf-8", columns=KOL)
    print(f"\nyazildi: {CIKTI.name} ({len(yeni):,} olay, "
          f"{yeni['tarih'].min()} .. {yeni['tarih'].max()})")


if __name__ == "__main__":
    main()
