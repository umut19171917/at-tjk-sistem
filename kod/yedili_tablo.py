"""
yedili_tablo.py — 7'Lİ GANYAN olay tablosunu ham arsivden uretir (K117 hazirligi).
OFFLINE: yalnizca veri/ham/ okunur; MEVCUT hicbir dosya DEGISTIRILMEZ.
Cikti: veri/yedili_tam.csv (YENI dosya; altili_tam.csv'nin 7 ayakli muadili).

NEDEN: 7'li Ganyan 2026'da cikmis YENI bir urun (K85: 2021-25 kartlarinin %0'i, 2026'nin %75'i).
Yeni urun = kalabalik henuz kalibre olmamis olabilir; ayrica devir orani cok yuksek
(2026'da 275 odeme / 123 devir = %31) -> devir sorusu da BU urunde olculebilir hale geliyor
(Altili'da OOS'ta yalniz ~11 devir var, guc yok).

AYAK ESLEMESI (uydurma yok, feed soyluyor):
  program/{ymd}/{pist}.json -> BAHISLER_TR icinde "7'Li GANYAN bu kosudan baslar" isareti
  hangi kosuda ise, 7'li o kosudan baslar ve ARDISIK 7 kosuyu kapsar.
  DOGRULAMA: sonuc feed'indeki odeme kombosu 7 parcalidir ve son 6 parcasi ayni kartin
  2. Altilisinin kombosuyla ortusur (31.01.2026 ISTANBUL'da birebir dogrulandi:
  7'li 4/7/11/3/4/8/2, 2. Altili 7/11/3/4/8/2).

CIKTI SUTUNLARI: tarih, sehir, leg1..leg7 (race_kod), t7_div, t7_devir, kombo
  t7_div dolu  -> odendi (1 birim basina TL)
  t7_devir dolu-> kimse bilemedi, sonraki yerli yaris gununun AYNI oyununa devretti
                  (resmi kural, K86 web dogrulamasi)
Elle: python yedili_tablo.py
"""
import json
import os
import re
import sys
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parent.parent
HAM = KOK / "veri" / "ham"
CIKTI = KOK / "veri" / "yedili_tam.csv"

PAT_ODEME = re.compile(r"7'L[İIi]\s*GANYAN\(([\d/,]+)\):\s*([\d.,]+)\s*TL")
PAT_DEVIR = re.compile(r"7'L[İIi]\s*GANYAN\(([\d/,]+)\):\s*Bilen\s*\S*\s*,\s*([\d.,]+)\s*TL\s*dev")
PAT_BASLA = re.compile(r"7'L[İIi]\s*GANYAN\s*bu\s*ko\S*udan\s*ba\S*lar", re.I)


def vfloat(s):
    s = str(s).strip()
    s = s.replace(".", "").replace(",", ".") if ("," in s and "." in s) else s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def kart_isle(ymd, pist):
    """Bir kart -> (satir dict) veya None. Hicbir sey uydurulmaz; eksikse None doner."""
    pp = HAM / "program" / f"{ymd}_{pist}.json"
    sp = HAM / "sonuclar" / f"{ymd}_{pist}.json"
    if not pp.exists() or not sp.exists():
        return None, "dosya yok"
    try:
        prog = json.load(open(pp, encoding="utf-8"))
        son = json.load(open(sp, encoding="utf-8"))
    except Exception as e:
        return None, f"okunamadi ({type(e).__name__})"

    # 1) baslangic kosusu (program feed'i soyluyor)
    bas_no = None
    for k in prog.get("kosular", []):
        if PAT_BASLA.search(k.get("BAHISLER_TR") or ""):
            bas_no = pd.to_numeric(k.get("RACENO"), errors="coerce")
            break
    if bas_no is None or pd.isna(bas_no):
        return None, "baslangic isareti yok"
    bas_no = int(bas_no)

    # 2) odeme/devir (sonuc feed'i)
    tam = " ".join(k.get("BAHISLER_TR") or "" for k in son.get("kosular", []))
    div = devir = kombo = None
    m = PAT_DEVIR.search(tam)
    if m:
        kombo, devir = m.group(1), vfloat(m.group(2))
    else:
        m = PAT_ODEME.search(tam)
        if m:
            kombo, div = m.group(1), vfloat(m.group(2))
    if kombo is None:
        return None, "odeme/devir satiri yok"
    if len(kombo.split("/")) != 7:
        return None, f"kombo 7 ayak degil ({len(kombo.split('/'))})"

    # 3) ardisik 7 kosunun race_kod'u (program feed'inden, RACENO sirasiyla)
    kos = {}
    for k in prog.get("kosular", []):
        n = pd.to_numeric(k.get("RACENO"), errors="coerce")
        kd = pd.to_numeric(k.get("KOD"), errors="coerce")
        if pd.notna(n) and pd.notna(kd):
            kos[int(n)] = int(kd)
    legs = [kos.get(bas_no + i) for i in range(7)]
    if any(x is None for x in legs):
        return None, "7 ardisik kosu bulunamadi"

    tarih = None
    for k in prog.get("kosular", []):
        if k.get("TARIH"):
            tarih = k["TARIH"]
            break
    return dict(tarih=tarih, sehir=pist, **{f"leg{i+1}": legs[i] for i in range(7)},
                t7_div=div, t7_devir=devir, kombo=kombo, bas_kosu=bas_no), None


def main():
    dosyalar = sorted((HAM / "sonuclar").glob("*.json"))
    satir, hata = [], {}
    for f in dosyalar:
        ad = f.stem
        if "_" not in ad:
            continue
        ymd, pist = ad.split("_", 1)
        r, e = kart_isle(ymd, pist)
        if r:
            satir.append(r)
        elif e and e != "odeme/devir satiri yok":
            hata[e] = hata.get(e, 0) + 1
    if not satir:
        print("7'li olayi bulunamadi."); return
    D = pd.DataFrame(satir)
    D.to_csv(CIKTI, index=False, encoding="utf-8")
    print(f"YAZILDI -> {CIKTI.name}: {len(D)} olay")
    D["dt"] = pd.to_datetime(D.tarih, format="%d/%m/%Y", errors="coerce")
    print(f"  tarih araligi: {D.dt.min().date()} .. {D.dt.max().date()}")
    print(f"  odenen: {D.t7_div.notna().sum()} | devir: {D.t7_devir.notna().sum()} "
          f"(%{100*D.t7_devir.notna().mean():.0f})")
    print(f"  temettu: medyan {D.t7_div.median():,.0f} TL | en buyuk {D.t7_div.max():,.0f} TL")
    print(f"  devir  : medyan {D.t7_devir.median():,.0f} TL | en buyuk {D.t7_devir.max():,.0f} TL")
    print(f"\n  pist dagilimi: {D.sehir.value_counts().to_dict()}")
    if hata:
        print(f"\n  atlanan kartlar: {hata}")

    # ---- CAPRAZ DOGRULAMA: 7'li kombosunun son 6'si, ayni kartin bir Altilisiyla ortusuyor mu?
    at = pd.read_csv(KOK / "veri" / "altili_tam.csv", low_memory=False)
    at["anahtar"] = at.tarih.astype(str) + "|" + at.sehir.astype(str)
    grp = {k: g for k, g in at.groupby("anahtar")}
    kontrol = tut = 0
    for r in D.itertuples():
        g = grp.get(f"{r.tarih}|{r.sehir}")
        if g is None:
            continue
        son6 = set(getattr(r, f"leg{i}") for i in range(2, 8))
        for a in g.itertuples():
            if set(int(getattr(a, f"leg{i}")) for i in range(1, 7)) == son6:
                tut += 1
                break
        kontrol += 1
    print(f"\n  CAPRAZ DOGRULAMA: {kontrol} olayda Altili karsilastirmasi yapildi; "
          f"7'linin son 6 ayagi bir Altiliyla BIREBIR ortusen: {tut} (%{100*tut/max(kontrol,1):.0f})")
    print("  (yuksek olmasi beklenir: 7'li genelde 2. Altili'nin bir onceki kosusuyla baslar)")


if __name__ == "__main__":
    main()
