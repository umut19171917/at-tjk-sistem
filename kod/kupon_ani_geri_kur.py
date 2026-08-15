"""
kupon_ani_geri_kur.py — K97: GECMIS Altililar icin "kupon ani" siralamasini geri kurar.

NEDEN: altili.html'deki sistem sirasi defter'den gelir, defter ise kosuya 5 dk kala yazilir.
Kupon ise Altili'nin ILK ayagindan ~30 dk once TEK seferde kurulur -> 6. ayagin karari
2-3 saat onceden verilmis olur. Iki siralama ayni degildir:
  09.08 Istanbul 2. Altili (kupon 15:14) — kosu 8'de piyasa sirasi 13 atin 13'unde degisti;
  kazanan #5 kupon aninda sistemin 2. atiydi, sayfada "sistem 10." goruluyor.
10 Agu'dan itibaren kupon ani vektoru altili_canli.kupon_hazirla icinde AYNEN kaydediliyor
(kaynak='canli'). Bu betik yalnizca ONCEKI gunler icin, kayitli verilerden geri kurar
(kaynak='geri_kurulan') ve sayfada AYRI etiketle gosterilir — uydurma degil, ama olcum
dosyasi olarak canli kayitla ayni raftadir sayilmaz.

GERI KURMA ZINCIRI (hepsi kayitli veri; yeniden fit YOK):
  bot1      <- defter.csv         (orana bakmaz, zamandan bagimsiz; kupon aninda da aynidir)
  p_kamu    <- altili_oran_log.csv (kupon anina EN YAKIN anlik goruntunun ganyanindan de-vig)
  alpha/gam <- raporlar/gunluk/*.txt basligi ("[Ingiliz: a=+0.24 g=+0.94 | Arap: ...]")
  bot2       = softmax(alpha*ln bot1 + gamma*ln p_kamu)   [gunluk.py ile ayni formul]

BILINEN SINIR: kadro degisikligi (kosmaz) sonrasi bot1 yeniden normalize edilmis olabilir;
o ayaklarda geri kurulan siralama kucuk sapma tasir. 20-24 Tem'de oran_log yok -> geri
kurulamaz, sayfada "kupon ani kaydi yok" yazar (UYDURULMAZ).

Elle: python kupon_ani_geri_kur.py            (yalniz eksikleri tamamlar)
      python kupon_ani_geri_kur.py --hepsi    (geri kurulanlarin tamamini yeniden uretir)
"""
import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from altili_canli import KUPON_ANI, KOL_ANI  # noqa: E402

ORAN_LOG = KOK / "veri" / "altili_oran_log.csv"
KUPON = KOK / "veri" / "altili_kupon.csv"
DEFTER = KOK / "veri" / "defter.csv"
GUNLUK = KOK / "raporlar" / "gunluk"
PAT_KAT = re.compile(r"Ingiliz:\s*a=([+-]?[\d.]+)\s*g=([+-]?[\d.]+)\s*\|\s*"
                     r"Arap:\s*a=([+-]?[\d.]+)\s*g=([+-]?[\d.]+)")


def katsayilar():
    """tarih -> {'Ingiliz': (a,g), 'Arap': (a,g)}  — gunluk rapor basliklarindan okunur."""
    out = {}
    for p in sorted(GUNLUK.glob("*.txt")):
        tarih = p.name[:10]
        if tarih in out:
            continue
        m = PAT_KAT.search(p.read_text(encoding="utf-8", errors="ignore"))
        if m:
            out[tarih] = {"Ingiliz": (float(m.group(1)), float(m.group(2))),
                          "Arap": (float(m.group(3)), float(m.group(4)))}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hepsi", action="store_true",
                    help="daha once geri kurulanlari da yeniden uret")
    args = ap.parse_args()

    if not ORAN_LOG.exists():
        print("altili_oran_log.csv yok -> geri kurulamaz.")
        return

    kat = katsayilar()
    print(f"katsayi okunan gun: {len(kat)}  ({min(kat) if kat else '-'} .. {max(kat) if kat else '-'})")

    o = pd.read_csv(ORAN_LOG, low_memory=False)
    o["ts"] = pd.to_datetime(o["kayit_ts"], errors="coerce")
    for c in ["seq", "ayak", "kosu_no", "race_kod", "no", "ganyan", "dk_kala", "kosmaz"]:
        o[c] = pd.to_numeric(o[c], errors="coerce")
    o = o[(o["kosmaz"] != 1) & (o["ganyan"] > 0)]

    d = pd.read_csv(DEFTER, low_memory=False)
    for c in ["race_kod", "no", "bot1"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d[["race_kod", "no", "bot1", "at_ad", "irk"]].drop_duplicates(["race_kod", "no"])

    k = pd.read_csv(KUPON, low_memory=False)
    k["seq"] = pd.to_numeric(k["seq"], errors="coerce")
    kupon_ts = (k.groupby(["tarih", "pist", "seq"])["kayit_ts"].min().reset_index()
                 .rename(columns={"kayit_ts": "kupon_ts"}))
    kupon_ts["kupon_ts"] = pd.to_datetime(kupon_ts["kupon_ts"], errors="coerce")

    var = pd.DataFrame(columns=KOL_ANI)
    if KUPON_ANI.exists():
        var = pd.read_csv(KUPON_ANI, low_memory=False)
        var["seq"] = pd.to_numeric(var["seq"], errors="coerce")
        if args.hepsi:
            var = var[var["kaynak"] != "geri_kurulan"]
    # Anahtar AYAK duzeyinde: yarim kalmis pencereler (or. kupon kurulurken oran gunlugu
    # heniz son ayaklari loglamamis) tamamlanabilsin. Pencere duzeyinde anahtarlamak
    # 09.08 Izmir 2. Altili'sinda 1. ayak yazilinca digerlerini kalici olarak disarida
    # birakmisti -- bu yuzden ayak bazina indirildi.
    var["ayak"] = pd.to_numeric(var["ayak"], errors="coerce") if len(var) else None
    mevcut = (set(zip(var["tarih"].astype(str), var["pist"], var["seq"], var["ayak"]))
              if len(var) else set())

    satirlar, atlanan = [], []
    for _, w in kupon_ts.iterrows():
        anahtar = (str(w["tarih"]), w["pist"], w["seq"])
        if all(anahtar + (float(i),) in mevcut for i in range(1, 7)):
            continue
        if pd.isna(w["kupon_ts"]):
            atlanan.append((anahtar, "kupon kayit_ts okunamadi")); continue
        kg = kat.get(str(w["tarih"]))
        if kg is None:
            atlanan.append((anahtar, "gunluk raporda katsayi yok")); continue
        og = o[(o["tarih"].astype(str) == str(w["tarih"])) & (o["pist"] == w["pist"])
               & (o["seq"] == w["seq"])]
        if og.empty:
            atlanan.append((anahtar, "oran_log kaydi yok")); continue

        for ayak, ga in og.groupby("ayak"):
            if anahtar + (float(ayak),) in mevcut:
                continue                      # o ayak zaten kayitli (canli veya geri kurulmus)
            ga = ga.copy()
            ga["fark"] = (ga["ts"] - w["kupon_ts"]).abs()
            snap = ga[ga["ts"] == ga.loc[ga["fark"].idxmin(), "ts"]]
            m = snap.merge(d, on=["race_kod", "no"], how="left", suffixes=("", "_d"))
            m = m[m["bot1"].notna() & (m["bot1"] > 0)]
            if len(m) < 4:
                continue
            irk = str(m["irk"].mode().iloc[0]) if m["irk"].notna().any() else "Ingiliz"
            a, g = kg.get(irk, kg["Ingiliz"])
            ham = 1.0 / m["ganyan"].values
            p_kamu = ham / ham.sum()
            s = a * np.log(m["bot1"].values + 1e-12) + g * np.log(p_kamu + 1e-12)
            e = np.exp(s - s.max())
            bot2 = e / e.sum()
            for i, (_, r) in enumerate(m.iterrows()):
                satirlar.append({
                    "kayit_ts": f"{snap['ts'].iloc[0]:%Y-%m-%d %H:%M}",
                    "tarih": w["tarih"], "pist": w["pist"], "seq": int(w["seq"]),
                    "dk_grup": 30,          # K105: geri kurulanlarin tamami 30 dk grubudur
                    "ayak": int(ayak), "kosu_no": r.get("kosu_no"),
                    "race_kod": r.get("race_kod"), "saat": r.get("saat"),
                    "dk_kala": r.get("dk_kala"), "no": int(r["no"]),
                    "at_ad": r.get("at_ad") if pd.notna(r.get("at_ad")) else r.get("at_ad_d"),
                    "bot1": r["bot1"], "bot2": bot2[i], "kamu": p_kamu[i],
                    "oran": r["ganyan"], "kaynak": "geri_kurulan"})

    if not satirlar:
        print("geri kurulacak yeni Altili yok.")
    else:
        yeni = pd.DataFrame(satirlar)
        cikti = pd.concat([var, yeni], ignore_index=True) if len(var) else yeni
        cikti.reindex(columns=KOL_ANI).to_csv(KUPON_ANI, index=False, encoding="utf-8")
        n = yeni.groupby(["tarih", "pist", "seq"]).ngroups
        print(f"geri kuruldu: {n} Altili, {len(yeni)} satir -> {KUPON_ANI.name}")

    if atlanan:
        print(f"\ngeri kurulAMAYAN {len(atlanan)} Altili (sayfada 'kupon ani kaydi yok' yazar):")
        for (t, p, s), sebep in atlanan[:30]:
            print(f"   {t} {p} {int(s)}. Altili -> {sebep}")


if __name__ == "__main__":
    main()
