"""
altili_v3_test.py — "BANKER HAK EDILSIN" varyantinin backtesti (K115 adayi).
OFFLINE, SALT-OKUNUR: canliya DOKUNMAZ, hicbir dosyaya yazmaz.

NEREDEN GELDI: BEKLEYENLER #9'un UCUNCU adayi (31 Tem'de yazildi, o gun kanit yoktu).
K114 (24 Agu) o kaniti verdi — 546 canli tek-at ayaginda:
  banker bayragi tasiyan (p_tepe >= BANKER_ESIK) : %52,1 isabet  (taban %33)
  bayrak tasimayan tek-at                        : %30,4 isabet  (tabanin ALTINDA)
  Fisher p=0,0001
Yani acgozlunun tek-at kararlarinin cogu guven degil, butce artigi (K88: genislik = butcenin
6. koku). v3 yalnizca O ayaklari kapatir: hak edilmemis ayak taban 2 attan baslar.

TASARIM ONCEDEN SABIT (sonuca gore degistirilmeyecek):
  kupon_kur_acgozlu_v3(ayak, max_kombo, BANKER_ESIK)  [altili_backtest.py — tek kaynak]
  Yeni sabit YOK: BANKER_ESIK zaten sistemde kullaniliyor. Baska varyant/tarama YAPILMAZ.

KARAR KRITERI (sonuc gorulmeden yazildi):
  v3 canliya ONERILIR <=> @900'de HEM ayak isabeti HEM 6/6 sayisi acgozlu900'den DUSUK DEGIL.
  Butce-ozgullugu (K98 dersi: v2'nin ustunlugu yalniz @900'deydi) GATE degil, TESHIS olarak
  raporlanir: @96 ve @288 de basilir.
  ROI bilgi amaclidir (hepsinin negatif olmasi bekleniyor; kesinti duvari yerinde).

ZEMIN: K110 sonrasi dogru fiyatlama (birim 1,25 TL; temettu birimle CARPILMAZ).
Sadece 6/6 oder (K57/K65 olcutu). OOS = 2025-26, EXCL pistler disarida.
Elle: python altili_v3_test.py
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from math import comb

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from altili_backtest import kupon_kur, kupon_kur_acgozlu, kupon_kur_acgozlu_v3  # noqa: E402
from altili_canli import BANKER_ESIK  # noqa: E402

EXCL = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA", "DBAKIR"}
BIRIM = 1.25
KAPSAM = 0.75
RNG = np.random.default_rng(20260824)
NBOOT = 3000


def kur(mod, aa, mk):
    if mod == "acgozlu":
        return kupon_kur_acgozlu(aa, mk)
    if mod == "v3":
        return kupon_kur_acgozlu_v3(aa, mk, BANKER_ESIK)
    return kupon_kur(aa, KAPSAM, mk, BANKER_ESIK)


def calis(olaylar, pmap, wmap, mk, mod):
    mal, g6, av = [], [], {}
    a6 = a5 = tut = top = 0
    tek_hak = tek_haksiz = 0
    div = []
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
        # tek-at ayaklarin hak edilmisligi (teshis)
        for i in range(6):
            if len(sec[i]) == 1:
                ptop = max(p for _, p in aa[i])
                if ptop >= BANKER_ESIK:
                    tek_hak += 1
                else:
                    tek_haksiz += 1
        t = [kaz[i] in sec[i] for i in range(6)]
        for i in range(6):
            av[(oi, i)] = int(t[i])
        h = sum(t)
        tut += h
        top += 6
        a6 += (h == 6)
        a5 += (h == 5)
        mal.append(int(np.prod([len(s) for s in sec])) * BIRIM)
        g = 0.0
        if h == 6 and pd.notna(o.get("t6_div")):
            g = float(o["t6_div"])
            div.append(g)
        g6.append(g)
    return dict(mal=np.array(mal), g6=np.array(g6), a6=a6, a5=a5, tut=tut, top=top,
                av=av, div=div, tek_hak=tek_hak, tek_haksiz=tek_haksiz)


def boot(mal, g6):
    if len(mal) == 0:
        return (float("nan"),) * 2
    idx = RNG.integers(0, len(mal), size=(NBOOT, len(mal)))
    r = (g6[idx].sum(1) - mal[idx].sum(1)) / mal[idx].sum(1) * 100
    return np.percentile(r, 2.5), np.percentile(r, 97.5)


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
    print(f"OOS olay: {len(oos)} | BANKER_ESIK={BANKER_ESIK} | birim {BIRIM} TL | sadece 6/6 oder")

    for mk in (900, 288, 96):
        print("\n" + "=" * 104)
        print(f"BUTCE {mk}" + ("   <-- KARAR BUTCESI" if mk == 900 else "   (teshis: butce-ozgullugu)"))
        print("=" * 104)
        print(f"{'dagitim':>10} {'olay':>5} {'ort.kombo':>9} {'ayak isabet':>12} {'6/6':>4} {'5/6':>4} "
              f"{'tek-at: hak/haksiz':>19} {'ROI%':>7} {'ROI %95 GA':>17} {'ort.temettu':>11}")
        S = {}
        for mod in ("acgozlu", "v3", "kapsam"):
            r = calis(oos, pmap, wmap, mk, mod)
            S[mod] = r
            roi = (r["g6"].sum() - r["mal"].sum()) / r["mal"].sum() * 100
            lo, hi = boot(r["mal"], r["g6"])
            tekat = f"{r['tek_hak']}/{r['tek_haksiz']}"
            print(f"{mod:>10} {len(r['mal']):>5} {r['mal'].sum()/len(r['mal'])/BIRIM:>9.0f} "
                  f"%{100*r['tut']/r['top']:>10.1f} {r['a6']:>4} {r['a5']:>4} "
                  f"{tekat:>19} {roi:>+7.1f} [{lo:>+6.1f},{hi:>+6.1f}] "
                  f"{(np.mean(r['div']) if r['div'] else 0):>11,.0f}")
        x, y, pv = mcnemar(S["v3"]["av"], S["acgozlu"]["av"])
        print(f"\n  esli ayak kiyasi v3 vs acgozlu: yalniz-v3 {x}, yalniz-acgozlu {y}, p={pv:.4f}")
        if mk == 900:
            ok1 = S["v3"]["tut"] / S["v3"]["top"] >= S["acgozlu"]["tut"] / S["acgozlu"]["top"]
            ok2 = S["v3"]["a6"] >= S["acgozlu"]["a6"]
            print(f"\n  KRITER @900: ayak isabeti [{'OK' if ok1 else 'KALDI'}]  "
                  f"6/6 [{'OK' if ok2 else 'KALDI'}]  ->  "
                  f"{'GECTI (canliya onerilebilir)' if ok1 and ok2 else 'GECILEMEDI (canliya ALINMAZ)'}")


if __name__ == "__main__":
    main()
