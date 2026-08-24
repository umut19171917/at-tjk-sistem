"""
yedili_test.py — 7'Lİ GANYAN kolu backtesti + DEVİR sorusu (K117 adayi).
OFFLINE, SALT-OKUNUR: canliya DOKUNMAZ, hicbir dosyaya yazmaz.

NEREDEN GELDI: K116'da dagitici kolu tukendi; kalan iki adres BILGI/URUN idi —
7'li ganyan (K85: 2026'da cikmis YENI urun) ve devir anlari (K84/K85/K86).
Ikisi TEK testte birlesiyor: 7'li'nin devir orani %31 (Altili'da %0,6) -> devir sorusu
Altili'da 11 gozleme sikisirken burada 123 gozlemle olculebiliyor.

VERI: veri/yedili_tam.csv (yedili_tablo.py uretti, 395 olay, ayak eslemesi %100 capraz
dogrulandi: her olayin son 6 ayagi bilinen bir Altiliyla birebir ortusuyor).

ADIL KIYAS — ESIT PARA, esit kombo DEGIL:
  Altili birim 1,25 TL · 7'li birim 2,00 TL (K86, TJK resmi).
  900 kombo Altili = 1.125 TL  ->  ayni parayla 7'li 562 kombo alinir.
  Esit-kombo kiyasi 7'liye HAKSIZ AVANTAJ verirdi (daha cok para harcamis olur).

EN GUCLU YAN: 7'li'nin son 6 ayagi ZATEN bir Altili. Yani AYNI kartta, AYNI kosularda,
AYNI modelle "6 ayak mi 7 ayak mi" sorusu ESLI olarak sorulabiliyor. Kart etkisi, gun etkisi,
model kalitesi otomatik sabitleniyor.

KARAR KRITERLERI (SONUC GORULMEDEN YAZILDI):
  (A) 7'li kolu ilerletmeye deger  <=>  esit parada 7'li'nin ROI'si, AYNI kartlarin
      Altili ROI'sinden ANLAMLI iyi (esli bootstrap %95 GA sifiri icermeyecek).
  (B) "devir sonrasi oyna" stratejisi deger  <=>  devirden HEMEN SONRAKI olaylarin ROI'si,
      normal olaylarin ROI'sinden ANLAMLI iyi (ayni test).
  Ikisi de negatif cikabilir; beklenti odur (kesinti duvari). Kriter "daha az kotu" degil,
  ANLAMLI FARK'tir. Kriter sonuca gore DEGISTIRILMEZ.

ONCEDEN YAZILAN BEKLENTI: 7 ayak, 6'dan yapisal olarak zor (genislik 7. kuvvetle buyur) ve
birim 1,6 kat pahali. "Yeni urun" avantajinin bunu asmasi icin cok buyuk olmasi gerekir ->
(A)'nin gecmesi BEKLENMIYOR. (B) icin beklenti yok: devreden para kesintisini zaten odemistir,
bu yapisal olarak gercek bir avantajdir; soru buyuklugunun olculebilir olup olmadigi.
Elle: python yedili_test.py
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from altili_backtest import kupon_kur  # noqa: E402
from altili_canli import BANKER_ESIK  # noqa: E402

EXCL = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA", "DBAKIR", "ANTALYA"}
B7, B6 = 2.00, 1.25          # birim fiyatlar (K86)
KAPSAM = 0.75
RNG = np.random.default_rng(20260824)
NBOOT = 4000


def kur_n(ayaklar, kapsam, max_kombo, banker):
    """kupon_kur'un N-ayakli hali (orijinali 6'ya sabit). Ayni mantik, ayni esikler."""
    sec = []
    for atlar in ayaklar:
        atlar = sorted([(n, p) for n, p in atlar if pd.notna(p) and p > 0], key=lambda x: -x[1])
        if not atlar:
            return None
        if atlar[0][1] >= banker:
            sec.append({atlar[0][0]}); continue
        kum, s = 0.0, []
        for no, p in atlar:
            s.append(no); kum += p
            if kum >= kapsam:
                break
        sec.append(set(s))
    while np.prod([len(s) for s in sec]) > max_kombo:
        i = max(range(len(sec)), key=lambda j: len(sec[j]))
        if len(sec[i]) <= 1:
            break
        a = sorted([(n, p) for n, p in ayaklar[i] if pd.notna(p) and p > 0], key=lambda x: -x[1])
        for no, _ in reversed(a):
            if no in sec[i]:
                sec[i].discard(no); break
    return sec


def kos(olaylar, pmap, wmap, nayak, para, birim, divcol):
    """Belirli PARA butcesiyle kupon kur. Doner: dizi halinde maliyet/getiri/isabet."""
    mk = int(para / birim)
    mal, get, alt = [], [], []
    for o in olaylar:
        ayak, kaz = [], []
        ok = True
        for i in range(nayak):
            rk = o.get(f"leg{i+1}")
            if pd.isna(rk):
                ok = False; break
            rk = int(rk)
            x, w = pmap.get(rk), wmap.get(rk)
            if not x or w is None:
                ok = False; break
            ayak.append(x); kaz.append(w)
        if not ok:
            continue
        sec = kur_n(ayak, KAPSAM, mk, BANKER_ESIK)
        if sec is None or any(len(s) == 0 for s in sec):
            continue
        h = all(kaz[i] in sec[i] for i in range(nayak))
        mal.append(int(np.prod([len(s) for s in sec])) * birim)
        d = o.get(divcol)
        get.append(float(d) if h and pd.notna(d) else 0.0)
        alt.append(1 if h else 0)
    return np.array(mal), np.array(get), np.array(alt)


def roi(m, g):
    return (g.sum() - m.sum()) / m.sum() * 100 if m.sum() else float("nan")


def esli_fark(m1, g1, m2, g2, ad):
    """1 eksi 2 icin esli bootstrap ROI farki."""
    n = min(len(m1), len(m2))
    if n < 10:
        print(f"    {ad}: n={n}, yetersiz"); return
    idx = RNG.integers(0, n, size=(NBOOT, n))
    r1 = (g1[idx].sum(1) - m1[idx].sum(1)) / m1[idx].sum(1) * 100
    r2 = (g2[idx].sum(1) - m2[idx].sum(1)) / m2[idx].sum(1) * 100
    d = r1 - r2
    lo, hi = np.percentile(d, 2.5), np.percentile(d, 97.5)
    print(f"    {ad}: {np.median(d):+.1f} puan  %95 GA [{lo:+.1f}, {hi:+.1f}]  "
          f"{'ANLAMLI' if lo > 0 or hi < 0 else 'sifiri iceriyor'}")
    return lo, hi


def main():
    p = pd.read_csv(KOK / "veri" / "altili_olasilik_bot1.csv", low_memory=False)
    pmap, wmap = {}, {}
    for rk, g in p.groupby("race_kod"):
        pmap[rk] = list(zip(g["no"], g["bot2"]))
        w = g.loc[g["kazandi"] == 1, "no"]
        if len(w):
            wmap[rk] = int(w.iloc[0])

    Y = pd.read_csv(KOK / "veri" / "yedili_tam.csv", low_memory=False)
    Y["dt"] = pd.to_datetime(Y.tarih, format="%d/%m/%Y", errors="coerce")
    Y = Y[~Y.sehir.isin(EXCL)].sort_values("dt").reset_index(drop=True)
    print(f"7'li olay (EXCL disi): {len(Y)} | {Y.dt.min().date()} .. {Y.dt.max().date()}")
    print(f"  odenen {Y.t7_div.notna().sum()} | devir {Y.t7_devir.notna().sum()}")

    # ---- ayni kartin Altilisi (7'linin son 6 ayagi) ----
    A = Y.copy()
    for i in range(1, 7):
        A[f"leg{i}"] = Y[f"leg{i+1}"]
    at = pd.read_csv(KOK / "veri" / "altili_tam.csv", low_memory=False)
    at["k"] = at.tarih.astype(str) + "|" + at.sehir.astype(str) + "|" + at.leg1.astype(str)
    dmap = {r.k: r.t6_div for r in at.itertuples()}
    A["t6_div"] = [dmap.get(f"{r.tarih}|{r.sehir}|{int(r.leg2)}") for r in Y.itertuples()]
    print(f"  eslesen Altili temettusu bulunan: {A.t6_div.notna().sum()}/{len(A)}")

    print("\n" + "=" * 98)
    print("A) 6 AYAK mi 7 AYAK mi — AYNI kart, AYNI kosular, ESIT PARA")
    print("=" * 98)
    yo, ao = Y.to_dict("records"), A.to_dict("records")
    for para in (1125.0, 2250.0, 360.0):
        print(f"\n  BUTCE {para:,.0f} TL/olay  (Altili {int(para/B6)} kombo · 7'li {int(para/B7)} kombo)")
        m6, g6, a6 = kos(ao, pmap, wmap, 6, para, B6, "t6_div")
        m7, g7, a7 = kos(yo, pmap, wmap, 7, para, B7, "t7_div")
        print(f"    {'Altili (6)':>12}: olay {len(m6):>3} | tutan {int(a6.sum()):>3} | "
              f"maliyet {m6.sum():>10,.0f} | getiri {g6.sum():>11,.0f} | ROI {roi(m6,g6):>+7.1f}%")
        print(f"    {'7li (7)':>12}: olay {len(m7):>3} | tutan {int(a7.sum()):>3} | "
              f"maliyet {m7.sum():>10,.0f} | getiri {g7.sum():>11,.0f} | ROI {roi(m7,g7):>+7.1f}%")
        r = esli_fark(m7, g7, m6, g6, "KRITER A (7li eksi Altili)")
        if para == 1125.0 and r:
            lo, hi = r
            print(f"    ==> KRITER A: {'GECTI' if lo > 0 else 'GECILEMEDI'}")

    print("\n" + "=" * 98)
    print("B) DEVIR SONRASI OYNAMAK — devirden hemen sonraki olay vs normal olaylar")
    print("=" * 98)
    Y2 = Y.reset_index(drop=True)
    sonra = np.zeros(len(Y2), dtype=bool)
    for i in range(len(Y2) - 1):
        if pd.notna(Y2.at[i, "t7_devir"]):
            sonra[i + 1] = True
    Y2["devir_sonrasi"] = sonra
    print(f"  devir-sonrasi olay: {int(sonra.sum())} | normal: {int((~sonra).sum())}")
    print(f"  devir-sonrasi temettu medyani: {Y2[sonra].t7_div.median():,.0f} TL"
          f"  | normal: {Y2[~sonra].t7_div.median():,.0f} TL")
    for para in (1125.0, 2250.0):
        ms, gs, asx = kos(Y2[sonra].to_dict("records"), pmap, wmap, 7, para, B7, "t7_div")
        mn, gn, an = kos(Y2[~sonra].to_dict("records"), pmap, wmap, 7, para, B7, "t7_div")
        print(f"\n  BUTCE {para:,.0f} TL/olay")
        print(f"    {'devir sonrasi':>14}: olay {len(ms):>3} | tutan {int(asx.sum()):>2} | "
              f"ROI {roi(ms,gs):>+7.1f}%")
        print(f"    {'normal':>14}: olay {len(mn):>3} | tutan {int(an.sum()):>2} | "
              f"ROI {roi(mn,gn):>+7.1f}%")
        # eslesmemis kiyas -> bagimsiz bootstrap farki
        if len(ms) >= 10 and len(mn) >= 10:
            i1 = RNG.integers(0, len(ms), size=(NBOOT, len(ms)))
            i2 = RNG.integers(0, len(mn), size=(NBOOT, len(mn)))
            r1 = (gs[i1].sum(1) - ms[i1].sum(1)) / ms[i1].sum(1) * 100
            r2 = (gn[i2].sum(1) - mn[i2].sum(1)) / mn[i2].sum(1) * 100
            d = r1 - r2
            lo, hi = np.percentile(d, 2.5), np.percentile(d, 97.5)
            print(f"    KRITER B (devir-sonrasi eksi normal): {np.median(d):+.1f} puan "
                  f"%95 GA [{lo:+.1f}, {hi:+.1f}]  "
                  f"{'ANLAMLI -> GECTI' if lo > 0 else 'sifiri iceriyor -> GECILEMEDI'}")


if __name__ == "__main__":
    main()
