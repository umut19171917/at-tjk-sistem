"""
esit_ayak_test.py — "HER AYAKTA ESIT SAYIDA AT" varyantinin backtesti (K159 adayi).
OFFLINE, SALT-OKUNUR: canliya DOKUNMAZ, hicbir dosyaya yazmaz.

NEREDEN GELDI: kullanici 8 Eyl 2026'da sordu — "900'luk kuponlari her ayakta esit at
yazacak sekilde yapsaydik?". Canli sicilde (432 kupon / 137 olay) olculdu: 6/6 17->22,
net -300.214 TL -> -3.806 TL. AMA 22 isabet yalnizca 14 bagimsiz olay, tek bir olay
odulun %46'si, olay-bootstrap GA'si sifiri iceriyor. 137 olay bu soruyu KARARA BAGLAYAMAZ.
Bu test ayni soruyu 1.526 OOS olayda sorar (K115/K116 ile ayni tezgah).

MEKANIZMA IDDIASI (K88 + K114 zincirinin devami): 6/6 bir CARPIM'dir. Acgozlu dagitim
butcenin 6. kokunu esitsiz dagitir; canli sicilde ayaklarin %20,8'i tek atli ve o ayaklar
%36,4 tutuyor. Zayif halka carpimi oldurur. Esit dagitimda hicbir ayak %60'in altina inmez.

TASARIM ONCEDEN SABIT (sonuca gore degistirilmeyecek):
  kupon_kur_esit(ayak, max_kombo): k = max{k : k^6 <= max_kombo}; her ayakta puan-azalan ilk k at.
  @900 -> k=3 (729 kombo) | @288 -> k=2 (64) | @96 -> k=2 (64).
  Yeni sabit YOK, parametre taramasi YOK, varyant YOK. Secim sirasi degismez (bot2 azalan).

KARAR KRITERI (sonuc gorulmeden yazildi):
  Esit dagitim CIDDIYE ALINIR <=> @900'de HER IKISI birden:
    (a) 6/6 sayisi acgozlu@900'den YUKSEK, VE
    (b) ROI farkinin (esit - acgozlu) ESLI bootstrap %95 GA'si tamamen SIFIRIN USTUNDE.
  Ikisinden biri tutmazsa: canli 137 olaydaki bulgu ORNEKLEM SANSI sayilir, kol KAPANIR.
  AYAK ISABETI KAPI DEGIL, TANIDIR: esit-3 daha az at yazar (18 vs ~26), isabetinin dusuk
  cikmasi BEKLENIR; iddia zaten "ayak isabeti degil, carpim" uzerine kurulu.
  ROI'nin mutlak degeri kapi degil (kesinti duvari yerinde; hepsinin negatif olmasi beklenir).

ONCEDEN YAZILAN BEKLENTI: K115'te v3 (taban 2) @900'de acgozluyu GECEMEDI (-63,6 vs -63,4)
ama @96'da +26,4 puan getirdi -> kusur SIKISIK butcede ciddi, BOL butcede onemsiz. @900 bol
butcedir. Bu yuzden beklenti: esit-3 @900'de acgozluyu GECEMEZ. Canli bulgu buna ters;
1.526 olay hangisinin dogru oldugunu soyleyecek.

ZEMIN: K110 fiyatlama (birim 1,25 TL; temettu birimle CARPILMAZ). Sadece 6/6 oder.
OOS = 2025-26, EXCL pistler disarida.
UYARI (K130): arsiv backtestinde `ganyan_muhtemel` == kapanis -> piyasa terimi sizintili,
6/6 sayilari MUTLAK olarak sisik. Bu sisme HER IKI dagitimda da ayni yonde calisir; test
mutlak seviyeyi degil, ayni olaylarda IKI DAGITIMIN FARKINI olcer (K115/K116 ile ayni zemin).
Elle: python kod/esit_ayak_test.py
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from math import comb

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from altili_backtest import kupon_kur, kupon_kur_acgozlu  # noqa: E402
from altili_canli import BANKER_ESIK  # noqa: E402

EXCL = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA", "DBAKIR"}
BIRIM = 1.25
KAPSAM = 0.75
RNG = np.random.default_rng(20260908)
NBOOT = 4000


def esit_k(max_kombo):
    k = 1
    while (k + 1) ** 6 <= max_kombo:
        k += 1
    return k


def kupon_kur_esit(ayak_atlari, max_kombo):
    """Her ayakta AYNI sayida at: k = max{k : k^6 <= max_kombo}, puan-azalan ilk k."""
    k = esit_k(max_kombo)
    sec = []
    for a in ayak_atlari:
        sr = sorted([(no, p) for no, p in a if pd.notna(p) and p > 0], key=lambda x: -x[1])
        sec.append({no for no, _ in sr[:k]})
    return sec


def kur(mod, aa, mk):
    if mod == "acgozlu":
        return kupon_kur_acgozlu(aa, mk)
    if mod == "esit":
        return kupon_kur_esit(aa, mk)
    return kupon_kur(aa, KAPSAM, mk, BANKER_ESIK)


def calis(olaylar, pmap, wmap, mk, mod):
    mal, g6, av, div = [], [], {}, []
    a6 = a5 = tut = top = 0
    tekat = 0
    for oi, o in enumerate(olaylar):
        aa, kaz, ok = [], [], True
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
        tekat += sum(1 for s in sec if len(s) == 1)
        t = [kaz[i] in sec[i] for i in range(6)]
        for i in range(6):
            av[(oi, i)] = int(t[i])
        h = sum(t)
        tut += h
        top += 6
        a6 += (h == 6)
        a5 += (h == 5)
        mal.append(int(np.prod([len(s) for s in sec])) * BIRIM)
        g = float(o["t6_div"]) if (h == 6 and pd.notna(o.get("t6_div"))) else 0.0
        if h == 6 and g:
            div.append(g)
        g6.append(g)
    return dict(mal=np.array(mal), g6=np.array(g6), a6=a6, a5=a5, tut=tut, top=top,
                av=av, div=div, tekat=tekat)


def roi(r):
    return (r["g6"].sum() - r["mal"].sum()) / r["mal"].sum() * 100


def esli_boot(ra, rb):
    """AYNI olaylarda esli ROI farki (esit - acgozlu). Iki kol ayni olay sirasinda calisir."""
    n = min(len(ra["mal"]), len(rb["mal"]))
    ma, ga = ra["mal"][:n], ra["g6"][:n]
    mb, gb = rb["mal"][:n], rb["g6"][:n]
    idx = RNG.integers(0, n, size=(NBOOT, n))
    fa = (ga[idx].sum(1) - ma[idx].sum(1)) / ma[idx].sum(1) * 100
    fb = (gb[idx].sum(1) - mb[idx].sum(1)) / mb[idx].sum(1) * 100
    d = fa - fb
    return d.mean(), np.percentile(d, 2.5), np.percentile(d, 97.5)


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
    print(f"OOS olay: {len(oos)} | birim {BIRIM} TL | sadece 6/6 oder | K130 uyarisi gecerli")

    for mk in (900, 288, 96):
        k = esit_k(mk)
        print("\n" + "=" * 108)
        print(f"BUTCE {mk} kombo   (esit dagitim: her ayakta {k} at = {k**6} kombo)"
              + ("   <-- KARAR BUTCESI" if mk == 900 else "   (teshis)"))
        print("=" * 108)
        print(f"{'dagitim':>10} {'olay':>5} {'ort.kombo':>9} {'ayak isabet':>12} {'6/6':>4} "
              f"{'5/6':>4} {'tek-at ayak':>12} {'ROI%':>7} {'ROI %95 GA':>17} {'ort.temettu':>11}")
        S = {}
        for mod in ("acgozlu", "esit", "kapsam"):
            r = calis(oos, pmap, wmap, mk, mod)
            S[mod] = r
            idx = RNG.integers(0, len(r["mal"]), size=(NBOOT, len(r["mal"])))
            rr = (r["g6"][idx].sum(1) - r["mal"][idx].sum(1)) / r["mal"][idx].sum(1) * 100
            print(f"{mod:>10} {len(r['mal']):>5} {r['mal'].sum()/len(r['mal'])/BIRIM:>9.0f} "
                  f"%{100*r['tut']/r['top']:>10.1f} {r['a6']:>4} {r['a5']:>4} {r['tekat']:>12} "
                  f"{roi(r):>+7.1f} [{np.percentile(rr, 2.5):>+6.1f},"
                  f"{np.percentile(rr, 97.5):>+6.1f}] "
                  f"{(np.mean(r['div']) if r['div'] else 0):>11,.0f}")
        d, lo, hi = esli_boot(S["esit"], S["acgozlu"])
        x, y, pv = mcnemar(S["esit"]["av"], S["acgozlu"]["av"])
        print(f"\n  ESLI ROI farki (esit - acgozlu): {d:+.1f} puan  %95 GA [{lo:+.1f}, {hi:+.1f}]")
        print(f"  esli ayak kiyasi: yalniz-esit {x}, yalniz-acgozlu {y}, p={pv:.4f}")
        print(f"  6/6: esit {S['esit']['a6']} vs acgozlu {S['acgozlu']['a6']}"
              f"  (fark {S['esit']['a6'] - S['acgozlu']['a6']:+d})")
        if mk == 900:
            a = S["esit"]["a6"] > S["acgozlu"]["a6"]
            b = lo > 0
            print(f"\n  KRITER @900: (a) 6/6 daha yuksek [{'OK' if a else 'KALDI'}]   "
                  f"(b) esli ROI GA'si sifirin ustunde [{'OK' if b else 'KALDI'}]")
            print(f"  -> {'CIDDIYE ALINIR' if a and b else 'GECILEMEDI: canli bulgu ORNEKLEM SANSI'}")


if __name__ == "__main__":
    main()
