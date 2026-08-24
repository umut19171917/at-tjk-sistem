"""
altili_saha_test.py — SAHA-ORANTILI genislik dagitimi backtesti (K116 adayi).
OFFLINE, SALT-OKUNUR: canliya DOKUNMAZ, hicbir dosyaya yazmaz.

NEREDEN GELDI: BEKLEYENLER #9'un DORDUNCU adayi (K88, 31 Tem). Olculen dayanak:
  kapsam ailesi sahayi HIC fiyatlamiyor — saha 4-7'den 12+'ya cikarken secilen at sayisi
  sabit (kor. -0,15..+0,17), cunku genislik = butcenin 6. koku. Oysa isabet %65,4 -> %36,4.
  Altili alti ayagi birden istedigi icin zincir en zayif halkayla belirlenir.

TASARIM ONCEDEN SABIT (sonuca gore degistirilmeyecek):
  kupon_kur_saha(ayak, max_kombo)  [altili_backtest.py — tek kaynak]
  Butce dolana dek kapsama orani (k_i/F_i) EN DUSUK ayaga bir at eklenir. Secim sirasi
  degismez (puan-azalan ilk k_i at). Tek degisen: GENISLIGIN DAGILIMI.
  Yeni sabit/parametre YOK. Varyant taramasi YAPILMAZ.

KARAR KRITERI (sonuc gorulmeden yazildi):
  saha canliya ONERILIR <=> @900'de HEM ayak isabeti HEM 6/6 sayisi KAPSAM@900'den
  (yani `genis900`, yerini alacagi config) DUSUK DEGIL.
  Acgozlu ile kiyas TESHIS amaclidir, gate degil.

ONCEDEN YAZILAN BEKLENTI: saha, olasilik dagiliminin yayvanliginin KABA vekilidir; gercek
dagilim zaten elimizde (acgozlu onu kullaniyor). Bu yuzden saha'nin ACGOZLUYU gecmesi
BEKLENMIYOR. Asil soru: sahayi hic gormeyen KAPSAM'i geciyor mu?

ZEMIN: K110 sonrasi dogru fiyatlama (birim 1,25 TL; temettu birimle CARPILMAZ).
Sadece 6/6 oder (K57/K65). OOS = 2025-26, EXCL pistler disarida.
Elle: python altili_saha_test.py
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from math import comb

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from altili_backtest import kupon_kur, kupon_kur_acgozlu, kupon_kur_saha  # noqa: E402
from altili_canli import BANKER_ESIK  # noqa: E402

EXCL = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA", "DBAKIR"}
BIRIM, KAPSAM = 1.25, 0.75
RNG = np.random.default_rng(20260824)
NBOOT = 4000
MODLAR = ("kapsam", "saha", "acgozlu")


def kur(mod, aa, mk):
    if mod == "kapsam":
        return kupon_kur(aa, KAPSAM, mk, BANKER_ESIK)
    if mod == "saha":
        return kupon_kur_saha(aa, mk)
    return kupon_kur_acgozlu(aa, mk)


def calis(olaylar, pmap, wmap, mk, mod):
    mal, g6, alti, av, div = [], [], [], {}, []
    tut = top = a6 = a5 = 0
    kucuk_at = kucuk_n = buyuk_at = buyuk_n = 0
    for oi, o in enumerate(olaylar):
        aa, kaz = [], []
        ok = True
        for i in range(6):
            rk = int(o[f"leg{i+1}"])
            x, w = pmap.get(rk), wmap.get(rk)
            if not x or w is None:
                ok = False
                break
            aa.append(x)
            kaz.append(w)
        if not ok:
            continue
        sec = kur(mod, aa, mk)
        if any(len(s) == 0 for s in sec):
            continue
        for i in range(6):                       # teshis: kucuk vs buyuk sahaya kac at
            F = len(aa[i])
            if F <= 7:
                kucuk_at += len(sec[i]); kucuk_n += 1
            elif F >= 12:
                buyuk_at += len(sec[i]); buyuk_n += 1
        t = [kaz[i] in sec[i] for i in range(6)]
        for i in range(6):
            av[(oi, i)] = int(t[i])
        h = sum(t)
        tut += h; top += 6; a6 += (h == 6); a5 += (h == 5)
        mal.append(int(np.prod([len(s) for s in sec])) * BIRIM)
        g = 0.0
        if h == 6 and pd.notna(o.get("t6_div")):
            g = float(o["t6_div"]); div.append(g)
        g6.append(g); alti.append(1 if h == 6 else 0)
    return dict(mal=np.array(mal), g6=np.array(g6), alti=np.array(alti), a6=a6, a5=a5,
                tut=tut, top=top, av=av, div=div,
                kucuk=kucuk_at / max(kucuk_n, 1), buyuk=buyuk_at / max(buyuk_n, 1))


def boot(mal, g6):
    idx = RNG.integers(0, len(mal), size=(NBOOT, len(mal)))
    r = (g6[idx].sum(1) - mal[idx].sum(1)) / mal[idx].sum(1) * 100
    return np.percentile(r, 2.5), np.percentile(r, 97.5)


def esli(A, B):
    """A - B icin esli bootstrap: ROI farki ve 6/6 farki."""
    n = min(len(A["mal"]), len(B["mal"]))
    idx = RNG.integers(0, n, size=(NBOOT, n))
    ra = (A["g6"][idx].sum(1) - A["mal"][idx].sum(1)) / A["mal"][idx].sum(1) * 100
    rb = (B["g6"][idx].sum(1) - B["mal"][idx].sum(1)) / B["mal"][idx].sum(1) * 100
    d = ra - rb
    d6 = A["alti"][idx].sum(1) - B["alti"][idx].sum(1)
    return (np.median(d), np.percentile(d, 2.5), np.percentile(d, 97.5),
            int(A["a6"] - B["a6"]), np.percentile(d6, 2.5), np.percentile(d6, 97.5))


def mcnemar(a, b):
    ort = set(a) & set(b)
    x = sum(1 for k in ort if a[k] == 1 and b[k] == 0)
    y = sum(1 for k in ort if a[k] == 0 and b[k] == 1)
    n = x + y
    p = 2 * sum(comb(n, i) for i in range(min(x, y) + 1)) / 2 ** n if n else 1.0
    return x, y, min(p, 1.0)


def main():
    p = pd.read_csv(KOK / "veri" / "altili_olasilik_bot1.csv", low_memory=False)
    pmap, wmap = {}, {}
    for rk, g in p.groupby("race_kod"):
        pmap[rk] = list(zip(g["no"], g["bot2"]))
        w = g.loc[g["kazandi"] == 1, "no"]
        if len(w):
            wmap[rk] = int(w.iloc[0])
    olay = pd.read_csv(KOK / "veri" / "altili_tam.csv", low_memory=False)
    olay["yil"] = pd.to_datetime(olay["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    olay = olay[~olay["sehir"].isin(EXCL)]
    oos = list(olay[olay.yil >= 2025].to_dict("records"))
    print(f"OOS olay: {len(oos)} | birim {BIRIM} TL | sadece 6/6 oder | kapsam={KAPSAM} banker={BANKER_ESIK}")

    for mk in (900, 288, 96):
        print("\n" + "=" * 106)
        print(f"BUTCE {mk}" + ("   <-- KARAR BUTCESI" if mk == 900 else "   (teshis)"))
        print("=" * 106)
        print(f"{'dagitim':>9} {'ort.kombo':>9} {'ayak isabet':>12} {'6/6':>4} {'5/6':>4} "
              f"{'kucuk saha at':>14} {'buyuk saha at':>14} {'ROI%':>7} {'ROI %95 GA':>17} {'ort.temettu':>11}")
        S = {}
        for mod in MODLAR:
            r = calis(oos, pmap, wmap, mk, mod)
            S[mod] = r
            roi = (r["g6"].sum() - r["mal"].sum()) / r["mal"].sum() * 100
            lo, hi = boot(r["mal"], r["g6"])
            print(f"{mod:>9} {r['mal'].sum()/len(r['mal'])/BIRIM:>9.0f} %{100*r['tut']/r['top']:>10.1f} "
                  f"{r['a6']:>4} {r['a5']:>4} {r['kucuk']:>14.2f} {r['buyuk']:>14.2f} "
                  f"{roi:>+7.1f} [{lo:>+6.1f},{hi:>+6.1f}] "
                  f"{(np.mean(r['div']) if r['div'] else 0):>11,.0f}")
        print("  (kucuk saha = <=7 atli ayak, buyuk saha = >=12 atli ayak: ortalama kac at yazildi)")
        for ref in ("kapsam", "acgozlu"):
            x, y, pv = mcnemar(S["saha"]["av"], S[ref]["av"])
            dm, dlo, dhi, d6, l6, h6 = esli(S["saha"], S[ref])
            print(f"\n  saha vs {ref:>8}: esli ayak yalniz-saha {x}, yalniz-{ref[:6]} {y}, p={pv:.4f}")
            print(f"  {'':17}ROI farki {dm:+.1f} puan [{dlo:+.1f},{dhi:+.1f}]"
                  f"{'  ANLAMLI' if dlo>0 or dhi<0 else '  sifiri iceriyor'}"
                  f" | 6/6 farki {d6:+d} [{l6:+.0f},{h6:+.0f}]"
                  f"{'  ANLAMLI' if l6>0 or h6<0 else '  sifiri iceriyor'}")
        if mk == 900:
            ok1 = S["saha"]["tut"] / S["saha"]["top"] >= S["kapsam"]["tut"] / S["kapsam"]["top"]
            ok2 = S["saha"]["a6"] >= S["kapsam"]["a6"]
            print(f"\n  KRITER @900 (kiyas: KAPSAM): ayak isabeti [{'OK' if ok1 else 'KALDI'}]  "
                  f"6/6 [{'OK' if ok2 else 'KALDI'}]  ->  "
                  f"{'GECTI (canliya onerilebilir)' if ok1 and ok2 else 'GECILEMEDI (canliya ALINMAZ)'}")


if __name__ == "__main__":
    main()
