# -*- coding: utf-8 -*-
"""
tek_kupon_19k.py — SORU: kupon akisinin ILK GUNUNDEN (20 Tem 2026) bugune, HER Altili'ya
tek bir 19.479 TL'lik kupon yatirmis olsaydik kac tanesini tutturur, ne kazanip kaybederdik?

19.479 TL nereden geliyor: K113. 5/6'da kalan 112 kuponun kacirilan ayagindaki kazanan
MEDYAN 5. siradaydi; "her ayakta derinlik 5" kuponunun ONCEDEN alinmasi Altili basina
ortalama 19.479 TL tutuyordu. Bu betik o rakami SABIT BUTCE olarak alip gercek sicile
uyguluyor. SALT-OKUNUR: hicbir veri dosyasina yazmaz.

YONTEM (kararlar sonuc gorulmeden sabitlendi):
  butce   : 19.479 TL/Altili -> max_kombo = floor(19479 / birim_fiyat(pist))
            (1,25 TL pistlerde 15.583 kombo; K113'un 15.583 ortalamasiyla birebir ayni)
  dagitim : ASIL = kupon_kur_acgozlu (K65, olcek-bagimsiz, isabet-maksimize)
            KONTROL = K113'un kendi yontemi: her ayakta esit derinlik (butceye sigan en buyugu)
  olasilik: KUPON ANI fotografi -- oncelik ani@30dk > ani@15dk > defter.csv
            (hicbiri kapanis orani kullanmaz; K130 sizintisi bu yola girmez)
  kazanan : altili_kupon.csv'deki `kazanan` (arsivde sonuc==1 olan tek at)
  odul    : altili_temettu.csv resmi temettu (1 birim). Devir yok (144/144 odendi).
  bedel   : GERCEK kombo x birim (butceyi asamaz, altinda kalabilir)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
import rapor_ortak as ro                                   # noqa: E402
from altili_backtest import kupon_kur_acgozlu              # noqa: E402

BUTCE = 19479.0
ILK_GUN = "2026-07-20"


# ------------------------------------------------------------------ olasilik kaynagi
def olasilik_havuzu():
    """(tarih,pist,seq,ayak) -> [(no, bot2)] ; kaynak etiketiyle. Oncelik: ani30>ani15>defter."""
    hav, kaynak = {}, {}
    a = pd.read_csv(KOK / "veri" / "altili_kupon_ani.csv", low_memory=False)
    a["bot2"] = pd.to_numeric(a["bot2"], errors="coerce")
    a = a[a["bot2"].notna() & (a["bot2"] > 0)]
    for dk, etiket in ((15.0, "ani15"), (30.0, "ani30")):        # 30 sonra yazilir = kazanir
        s = a[a["dk_grup"] == dk]
        for key, g in s.groupby(["tarih", "pist", "seq", "ayak"]):
            hav[key] = list(zip(g["no"].astype(int), g["bot2"].astype(float)))
            kaynak[key] = etiket
    return hav, kaynak


def defter_havuzu(legs):
    """Bosluklar icin defter.csv (kupon ani tahmin defteri)."""
    d = pd.read_csv(KOK / "veri" / "defter.csv", low_memory=False)
    d["bot2"] = pd.to_numeric(d["bot2"], errors="coerce")
    d = d[d["bot2"].notna() & (d["bot2"] > 0)]
    per = {rk: list(zip(g["no"].astype(int), g["bot2"].astype(float)))
           for rk, g in d.groupby("race_kod")}
    return per


# ------------------------------------------------------------------ dagiticilar
def esit_derinlik(ayak_atlari, max_kombo):
    """K113'un TARIF ETTIGI kupon: her ayakta derinlik 5 (kacirilan ayagin medyan sirasi).

    DIKKAT: 5^6 = 15.625 kombo x 1,25 = 19.531 TL, yani 19.479'u 52 TL asar. 19.479 rakami
    K113'te derinlik-5'in ORTALAMA bedeliydi (kucuk sahalarda kombo dusuyor), tavan degil.
    Butceyi tavan sayip 4'e dusurmek K113'un onerisini olcmek olmaz -- o yuzden derinlik 5
    sabit tutulur ve gercek ortalama bedel ayrica raporlanir."""
    sr = [sorted(a, key=lambda x: -x[1]) for a in ayak_atlari]
    return [set(no for no, _ in s[:5]) for s in sr]


# ------------------------------------------------------------------ ana
def main():
    kup = pd.read_csv(KOK / "veri" / "altili_kupon.csv", low_memory=False)
    tem = pd.read_csv(KOK / "veri" / "altili_temettu.csv")
    tem = tem[tem["tarih"] >= ILK_GUN]

    legs = (kup.dropna(subset=["kazanan"])
               .drop_duplicates(["tarih", "pist", "seq", "ayak"])
               [["tarih", "pist", "seq", "ayak", "race_kod", "kazanan"]])
    hav, kaynak = olasilik_havuzu()
    dft = defter_havuzu(legs)

    olaylar = []
    for _, t in tem.iterrows():
        key = (t["tarih"], t["pist"], int(t["seq"]))
        g = legs[(legs.tarih == key[0]) & (legs.pist == key[1]) & (legs.seq == key[2])]
        if len(g) != 6:
            continue
        ayak_atlari, kaynaklar, kazananlar = [], [], []
        for _, L in g.sort_values("ayak").iterrows():
            k4 = (key[0], key[1], key[2], int(L["ayak"]))
            if k4 in hav:
                ayak_atlari.append(hav[k4]); kaynaklar.append(kaynak[k4])
            elif int(L["race_kod"]) in dft:
                ayak_atlari.append(dft[int(L["race_kod"])]); kaynaklar.append("defter")
            else:
                ayak_atlari.append(None); kaynaklar.append("YOK")
            kazananlar.append(int(L["kazanan"]))
        olaylar.append(dict(key=key, atlar=ayak_atlari, kaynak=kaynaklar,
                            kazanan=kazananlar, temettu=float(t["temettu"])))

    tam = [o for o in olaylar if all(a is not None for a in o["atlar"])]
    print("=" * 96)
    print("TEK KUPON @ 19.479 TL — 20 Tem 2026'dan bugune, HER Altili'ya bir kupon")
    print("=" * 96)
    print(f"  sonuclanmis Altili (temettu kayitli) : {len(olaylar)}")
    print(f"  6 ayagi da kupon-ani olasiligi olan  : {len(tam)}")
    print(f"  kapsam disi (o gun sistem kaydi yok) : {len(olaylar) - len(tam)}")

    say = {}
    for o in tam:
        for k in o["kaynak"]:
            say[k] = say.get(k, 0) + 1
    print("  olasilik kaynagi (ayak)              : "
          + " · ".join(f"{k}:{v}" for k, v in sorted(say.items(), key=lambda x: -x[1])))

    for ad, fn in (("ACGOZLU (K65) — 19.479 TL TAVAN", kupon_kur_acgozlu),
                   ("ESIT DERINLIK 5 (K113'un tarifi)", esit_derinlik)):
        bedel = odul = 0.0
        isabet = 0
        dagilim = {i: 0 for i in range(7)}
        vurus, kayit = [], []
        for o in tam:
            birim = ro.birim_fiyat(o["key"][1])
            mk = int(BUTCE // birim)
            sec = fn(o["atlar"], mk)
            kombo = int(np.prod([len(s) for s in sec]))
            b = kombo * birim
            tut = sum(1 for s, w in zip(sec, o["kazanan"]) if w in s)
            dagilim[tut] += 1
            bedel += b
            kayit.append((b, o["temettu"] if tut == 6 else 0.0))
            if tut == 6:
                isabet += 1
                odul += o["temettu"]
                vurus.append((o["key"], o["temettu"], b))
        net = odul - bedel
        # olay duzeyinde onyukleme (10.000 tekrar) -- ROI'nin belirsizligi
        rng = np.random.default_rng(20260904)
        arr = np.array(kayit)                                  # [:,0]=bedel [:,1]=odul
        boot = []
        for _ in range(10000):
            i = rng.integers(0, len(arr), len(arr))
            boot.append(100 * (arr[i, 1].sum() - arr[i, 0].sum()) / arr[i, 0].sum())
        alt, ust = np.percentile(boot, [2.5, 97.5])
        print("\n" + "-" * 96)
        print(f"  {ad}")
        print("-" * 96)
        print(f"  tutan Altili        : {isabet} / {len(tam)}  (%{100*isabet/len(tam):.1f})")
        print(f"  toplam bedel        : {bedel:>16,.0f} TL   (ort {bedel/len(tam):,.0f}/kupon)")
        print(f"  toplam odul         : {odul:>16,.0f} TL")
        print(f"  NET                 : {net:>16,.0f} TL")
        print(f"  ROI                 : %{100*net/bedel:>15.1f}"
              f"   %95 GA [%{alt:.1f}, %{ust:.1f}]")
        print(f"  ayak isabet dagilimi: " + " · ".join(f"{i}/6:{dagilim[i]}" for i in range(7)))
        for k, t, b in vurus:
            print(f"      VURUS {k[0]} {k[1]} #{k[2]}  temettu {t:>12,.0f}  bedel {b:>10,.0f}")
    print("=" * 96)


if __name__ == "__main__":
    main()
