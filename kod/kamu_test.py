# -*- coding: utf-8 -*-
"""
kamu_test.py — "KAMUYA NE KADAR GUVENELIM?" iki olcum (K112). Salt offline, HICBIR
dosyaya YAZMAZ, canliya DOKUNMAZ.

Cikis noktasi (kullanici, 19 Agu 2026): ISTANBUL 2. Altili'nin 1. ayaginda kazanan at
AFRIKA ATESI kupon aninda KAMUDA 2. sirdaydi ama bot2 onu 8. siraya koydu ve `orta`
(2 at yazar) onu yazmadi. At kazandi, temettu 272.186 TL. Soru: "sistem kamuya yeterince
agirlik vermiyor olabilir mi, agirliklari degistirmeli miyiz?"

Iki ayri sey olculuyor:

  A — UZAK AYAKTA "KAMU" NE KADAR OLGUN?
      Kupon 1. ayaga ~30 dk kala kurulur; 6. ayak o an ~3 SAAT uzaktadir. TJK o an
      gercek bir piyasa veriyor (para var, oranlar hareket ediyor) ama o piyasa
      KAPANIS piyasasi degildir. Ne kadar degil? Kupon anindaki kamu siralamasi ile
      RESMI KAPANIS siralamasi arasindaki Spearman rho, ayak mesafesine gore.

  B — BOT1'IN SESI (alpha) DEGISSEYDI NE OLURDU?
      bot2 ~ bot1^alpha * kamu^gamma. Olculen (K110, taze veriyle): Ingiliz alpha=0,19 gamma=0,98.
      alpha=0 -> SAF KAMU. Her ayakta GENISLIK SABIT (gercekten yazdigimiz at sayisi);
      degisen tek sey cetvel. Isabet VE para birlikte basilir.

======================================================================================
ON-KAYITLI OLCUT — B icin (K33/K52 hindsight yasagi)
======================================================================================
TARAMA KARAR VERMEZ. 10 alpha degeri basiliyor ama "en iyi cikani sec" YASAKTIR --
10 degerden birinin en iyi cikmasi kacinilmazdir ve o secim overfit olur.
KARAR VEREN TEK KIYAS, IKI NOKTA: alpha=0 (saf kamu) vs alpha=0,19 (bugunku).
  - ISABET: eslesmis McNemar (tam binom). Guc esigi K107: uyumsuz cift >= 6.
  - PARA  : ganyan ROI farki, olay (ALTILI) duzeyinde %95 bootstrap GA.
            Fiyat RESMI KAPANIS (defter.ganyan_kapanis) -- K110: oran_log kapanisi
            hic gormedigi icin KULLANILMAZ.
>> "KAMUYA DAHA COK AGIRLIK VERMELIYIZ" denir ANCAK VE ANCAK saf kamu, bugunkunden
   HEM isabette anlamli iyi HEM parada anlamli iyi cikarsa. Yalniz biri yeterli degil:
   isabet artip para artmiyorsa bu "kalabaliga katilmak"tir (K98-h tavani), beceri degil.
======================================================================================
"""
import sys
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))

GAMMA = 0.98                 # K110 olculen (Ingiliz; K96 0,95 demisti, taze veriyle guncellendi)
ALPHA_SIMDI = 0.19           # K110 olculen (Ingiliz); ELLE SECILMEDI
ASGARI_UYUMSUZ = 6           # K107 guc esigi
TARAMA = (0.0, 0.10, 0.19, 0.35, 0.50, 0.75, 1.00, 1.50, 2.50, 99.0)


def mcnemar_p(a, b):
    n = a + b
    return min(1.0, 2 * sum(comb(n, i) for i in range(min(a, b) + 1)) / 2 ** n) if n else 1.0


def yukle():
    k = pd.read_csv(KOK / "veri" / "altili_kupon.csv", low_memory=False)
    k = k[k["sonuclandi"].notna() & k["kazanan"].notna()]
    for c in ("nat", "kazanan", "race_kod", "seq", "ayak"):
        k[c] = pd.to_numeric(k[c], errors="coerce")
    k = k[k["nat"].notna() & k["nat"].gt(0)]

    a = pd.read_csv(KOK / "veri" / "altili_kupon_ani.csv", low_memory=False)
    if "dk_grup" not in a.columns:
        a["dk_grup"] = 30
    for c in ("bot1", "kamu", "no", "race_kod", "dk_grup", "seq", "ayak", "dk_kala"):
        a[c] = pd.to_numeric(a[c], errors="coerce")
    a = a[a["dk_grup"] == 30]

    d = pd.read_csv(KOK / "veri" / "defter.csv", low_memory=False)
    for c in ("no", "race_kod", "ganyan_kapanis"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d[d["ganyan_kapanis"].notna() & d["ganyan_kapanis"].gt(0)]
    kap = {(int(r.race_kod), int(r.no)): float(r.ganyan_kapanis) for r in d.itertuples()}
    return k, a, kap


# ------------------------------------------------------------------ A
def olcum_a(a, kap):
    from scipy.stats import spearmanr
    print("=" * 100)
    print("A — UZAK AYAKTA 'KAMU' NE KADAR OLGUN? (kupon ani siralamasi vs RESMI KAPANIS)")
    print("=" * 100)
    sat = []
    for (t, p, s, rk), g in a.groupby(["tarih", "pist", "seq", "race_kod"]):
        g = g.dropna(subset=["kamu"])
        if len(g) < 5:
            continue
        g = g.copy()
        g["kapanis"] = [kap.get((int(rk), int(n)), np.nan) for n in g["no"]]
        g = g.dropna(subset=["kapanis"])
        if len(g) < 5:
            continue
        rho = spearmanr(g["kamu"].rank(ascending=False), g["kapanis"].rank()).statistic
        sat.append({"ayak": int(g["ayak"].iloc[0]), "dk_kala": float(g["dk_kala"].iloc[0]),
                    "rho": rho,
                    "fav_ayni": int(int(g.loc[g["kamu"].idxmax(), "no"])
                                    == int(g.loc[g["kapanis"].idxmin(), "no"]))})
    df = pd.DataFrame(sat)
    print(f"  olculen ayak: {len(df):,}\n")
    print(f"  {'ayak':>5} {'n':>5} {'ort. dk kala':>13} {'Spearman rho':>14} {'FAVORI AYNI':>13}")
    for ay, g in df.groupby("ayak"):
        print(f"  {ay:>5} {len(g):>5} {g.dk_kala.mean():>13.0f} {g.rho.mean():>14.3f} "
              f"{'%' + f'{100*g.fav_ayni.mean():.0f}':>13}")
    print("\n  rho=1 -> siralama aynen kaliyor · rho=0 -> hicbir iliski yok")
    print("  OKUMA: kupon aninda gordugumuz 'kamu', ODEYEN kamu DEGILDIR. 1. ayakta bile")
    print("  (postaya ~28 dk) favori yarisindan fazla degisiyor; 6. ayakta durum daha kotu.")
    return df


# ------------------------------------------------------------------ B
def ayak_havuzu(k, a, kap):
    ix = {key: g for key, g in a.groupby(["tarih", "pist", "seq", "race_kod"])}
    havuz = []
    for (t, p, s, rk), g in k.groupby(["tarih", "pist", "seq", "race_kod"]):
        tab = ix.get((t, p, int(s), int(rk)))
        if tab is None:
            continue
        tab = tab.dropna(subset=["bot1", "kamu"])
        if len(tab) < 5:
            continue
        kz = int(g["kazanan"].iloc[0])
        if kz not in set(tab["no"].astype(int)):
            continue
        b1 = np.maximum(tab["bot1"].values, 1e-12)
        km = np.maximum(tab["kamu"].values, 1e-12)
        nos = tab["no"].values.astype(int)
        oran = kap.get((int(rk), kz), np.nan)
        for gen in sorted(set(g["nat"].astype(int))):
            havuz.append({"olay": (t, p, int(s)), "b1": b1, "km": km, "nos": nos,
                          "kz": kz, "gen": int(gen), "oran": oran})
    return havuz


def sec(h, al):
    skor = np.log(h["b1"]) if al > 90 else al * np.log(h["b1"]) + GAMMA * np.log(h["km"])
    return h["kz"] in set(h["nos"][np.argsort(-skor)[:h["gen"]]])


def olcum_b(havuz):
    print("\n" + "=" * 100)
    print("B — BOT1'IN SESI (alpha) DEGISSEYDI? (genislik SABIT, fiyat RESMI KAPANIS)")
    print("=" * 100)
    print(f"  olculen (config x ayak) cifti: {len(havuz):,} | gamma={GAMMA} sabit\n")
    print(f"  {'alpha':>7} {'':>10} {'ayak isabeti':>13} {'tutan':>7} "
          f"{'ganyan ROI':>11} {'ort. kazanan oran':>18}")
    isabet = {}
    for al in TARAMA:
        h = np.array([sec(x, al) for x in havuz])
        isabet[al] = h
        yaz = sum(x["gen"] for x in havuz)
        oranlar = [x["oran"] for x, t in zip(havuz, h) if t and not np.isnan(x["oran"])]
        roi = (sum(oranlar) - yaz) / yaz * 100
        ad = {0.0: "SAF KAMU", ALPHA_SIMDI: "BUGUNKU", 99.0: "SAF BOT1"}.get(al, "")
        print(f"  {('inf' if al > 90 else f'{al:.2f}'):>7} {ad:>10} "
              f"{'%' + f'{100*h.mean():.1f}':>13} {int(h.sum()):>7} "
              f"{roi:>+10.1f}% {np.mean(oranlar) if oranlar else 0:>18.2f}")
    print("\n  !! TARAMA KARAR VERMEZ (K33/K52). 10 degerden birinin en iyi cikmasi kacinilmaz.")
    return isabet


def karar(havuz, isabet):
    print("\n" + "=" * 100)
    print("ON-KAYITLI KARAR KIYASI: SAF KAMU (alpha=0) vs BUGUNKU (alpha=0,19)")
    print("=" * 100)
    A, B = isabet[ALPHA_SIMDI], isabet[0.0]
    a_only, b_only = int((A & ~B).sum()), int((~A & B).sum())
    p = mcnemar_p(a_only, b_only)
    print(f"  ISABET: yalniz BUGUNKU {a_only} · yalniz SAF KAMU {b_only} · "
          f"uyumsuz {a_only + b_only} · McNemar p={p:.4f}")
    if a_only + b_only < ASGARI_UYUMSUZ:
        print(f"    -> BAKILAMAZ (uyumsuz < {ASGARI_UYUMSUZ}, K107)")
    elif p < 0.05:
        print(f"    -> FARK VAR, {'BUGUNKU' if a_only > b_only else 'SAF KAMU'} daha iyi")
    else:
        print("    -> fark kaniti yok")

    olaylar = sorted({x["olay"] for x in havuz})
    ix = {o: i for i, o in enumerate(olaylar)}
    oid = np.array([ix[x["olay"]] for x in havuz])
    gen = np.array([x["gen"] for x in havuz], dtype=float)
    orn = np.array([0.0 if np.isnan(x["oran"]) else x["oran"] for x in havuz])

    def roi_of(mask_olay, h):
        m = np.isin(oid, mask_olay)
        return (orn[m & h].sum() - gen[m].sum()) / gen[m].sum() * 100

    tum = np.arange(len(olaylar))
    r_now, r_kamu = roi_of(tum, A), roi_of(tum, B)
    rng = np.random.default_rng(23)
    bs = np.empty(4000)
    for i in range(4000):
        s = rng.integers(0, len(olaylar), len(olaylar))
        m = np.isin(oid, s)
        bs[i] = ((orn[m & A].sum() - gen[m].sum()) / gen[m].sum() * 100
                 - (orn[m & B].sum() - gen[m].sum()) / gen[m].sum() * 100)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    print(f"\n  PARA: BUGUNKU {r_now:+.1f}% · SAF KAMU {r_kamu:+.1f}% · "
          f"fark {r_now - r_kamu:+.2f} puan %95 GA [{lo:+.2f}, {hi:+.2f}]")
    print(f"    -> {'FARK VAR' if (lo > 0 or hi < 0) else 'PARA FARKI KANITI YOK (GA sifiri iceriyor)'}")
    print(f"    (referans: olculmus ganyan kesintisi -%28,3 — K104)")
    print("\n  HUKUM: 'kamuya daha cok agirlik verelim' ancak saf kamu HEM isabette HEM")
    print("  parada anlamli iyi cikarsa denir. Yukaridaki iki satira bak.")


def main():
    k, a, kap = yukle()
    olcum_a(a, kap)
    havuz = ayak_havuzu(k, a, kap)
    isabet = olcum_b(havuz)
    karar(havuz, isabet)


if __name__ == "__main__":
    main()
