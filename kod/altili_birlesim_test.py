"""
altili_birlesim_test.py — "IKI BOTU BIRLESTIRMEK TEK BOTTAN IYI MI?" backtesti (K90 adayi).
OFFLINE, SALT-OKUNUR: canliya DOKUNMAZ, hicbir dosyaya yazmaz.

NEREDEN GELDI (K89): 78 eslesmis canli ayakta kamu botlari ile bot1 TAMAMLAYICI cikti —
kamu favoride %85 / bot1 %73; surpriz 15+ oranda bot1 %42 / digerleri %25; bot1 13 benzersiz
ayak yakaladi, acgozlu 0. Kullanici birlesim kuponu istedi (butce 2x'e kadar cikabilir).

TASARIM (ONCEDEN SABIT — sonuca gore degistirilmeyecek):
  birlesim = kupon_kur_birlesim(bot2, bot1, max_kombo)  [altili_backtest.py, tek kaynak]
  her ayakta skor = max(bot1_norm, bot2_norm), normalize -> acgozlu dagitim.
  Aday canli config: birlesim1800 (butce 2x). Baska varyant taranMAZ (tek degisken ilkesi).

KONTROLLER (birlesimin degeri butceden mi mekanizmadan mi geliyor, ayirt etmek icin):
  - acgozlu900_bot2 / acgozlu900_bot1  : iki ebeveyn, canlideki halleriyle
  - acgozlu1800_bot2 / acgozlu1800_bot1: BUTCE kontrolu (ayni parayi tek bota ver)
  - birlesim900                        : esit-butce kontrolu (mekanizmanin saf etkisi)

KARAR KRITERI (ONCEDEN BAGLANDI, sonuc gorulmeden):
  birlesim1800 canliya alinir <=> OOS'ta hem AYAK ISABETI hem 6/6 SAYISI, 1800 butceli iki
  tek-bot kontrolunun IKISINDEN DE dusuk degilse. Dusukse birlesim mekanizmasi deger
  katmiyor demektir -> canliya alinmaz, K90'a "red" yazilir.
  ROI bilgi amaclidir (hepsinin negatif olmasi beklenir; ~%49 kesinti duvari yerinde, K52/K83).

DURUST ZEMIN: K57/K65 olcutu — sadece 6/6 oder, teselli yok. Birim 1,25 TL (EXCL pistler
zaten disarida, kalanlarin tamami 1,25 tarifesinde). OOS = 2025-26.
Elle: python altili_birlesim_test.py
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from math import comb

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from altili_backtest import kupon_kur_acgozlu, kupon_kur_birlesim  # noqa: E402

EXCL_SEHIR = {"ADANA", "ELAZIG", "DIYARBAKIR", "SANLIURFA", "DBAKIR"}
BIRIM = 1.25
RNG = np.random.default_rng(20260803)
NBOOT = 3000


def olay_sec(o, pm2, pm1, wmap, max_kombo, mod):
    """Tek olay icin secim kur. Doner (sec, kaz) veya None."""
    a2, a1, kaz = [], [], []
    for i in range(6):
        rk = int(o[f"leg{i+1}"])
        x2, x1, w = pm2.get(rk), pm1.get(rk), wmap.get(rk)
        if not x2 or not x1 or w is None:
            return None
        a2.append(x2); a1.append(x1); kaz.append(w)
    if mod == "bot2":
        sec = kupon_kur_acgozlu(a2, max_kombo)
    elif mod == "bot1":
        sec = kupon_kur_acgozlu(a1, max_kombo)
    else:
        sec = kupon_kur_birlesim(a2, a1, max_kombo)
    if any(len(s) == 0 for s in sec):
        return None
    return sec, kaz


def calis(olaylar, pm2, pm1, wmap, max_kombo, mod):
    mal, g6 = [], []
    a6 = a5 = ayak_tut = ayak_top = 0
    ayak_vec = {}                      # (olay_idx, ayak) -> tuttu (esli kiyas icin)
    div = []
    for oi, o in enumerate(olaylar):
        r = olay_sec(o, pm2, pm1, wmap, max_kombo, mod)
        if r is None:
            continue
        sec, kaz = r
        tut = [kaz[i] in sec[i] for i in range(6)]
        for i in range(6):
            ayak_vec[(oi, i)] = int(tut[i])
        t = sum(tut)
        ayak_tut += t; ayak_top += 6
        a6 += (t == 6); a5 += (t == 5)
        mal.append(int(np.prod([len(s) for s in sec])) * BIRIM)
        g = 0.0
        if t == 6 and pd.notna(o.get("t6_div")):
            g = float(o["t6_div"]); div.append(g)
        g6.append(g)
    return dict(mal=np.array(mal), g6=np.array(g6), a6=a6, a5=a5,
                ayak_tut=ayak_tut, ayak_top=ayak_top, av=ayak_vec, div=div)


def boot_roi(mal, g6):
    if len(mal) == 0:
        return (float("nan"),) * 2
    idx = RNG.integers(0, len(mal), size=(NBOOT, len(mal)))
    r = (g6[idx].sum(1) - mal[idx].sum(1)) / mal[idx].sum(1) * 100
    return np.percentile(r, 2.5), np.percentile(r, 97.5)


def mcnemar(av_a, av_b):
    ortak = set(av_a) & set(av_b)
    x = sum(1 for k in ortak if av_a[k] == 1 and av_b[k] == 0)
    y = sum(1 for k in ortak if av_a[k] == 0 and av_b[k] == 1)
    n = x + y
    p = 2 * sum(comb(n, i) for i in range(min(x, y) + 1)) / 2 ** n if n else 1.0
    return x, y, min(p, 1.0), len(ortak)


def main():
    p = pd.read_csv(KOK / "veri" / "altili_olasilik_bot1.csv", low_memory=False)
    pm1, pm2, wmap = {}, {}, {}
    for rk, g in p.groupby("race_kod"):
        pm1[rk] = list(zip(g["no"], g["bot1"]))
        pm2[rk] = list(zip(g["no"], g["bot2"]))
        w = g.loc[g["kazandi"] == 1, "no"]
        if len(w):
            wmap[rk] = int(w.iloc[0])

    olay = pd.read_csv(KOK / "veri" / "altili_tam.csv", low_memory=False)
    olay["yil"] = pd.to_datetime(olay["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    olay = olay[~olay["sehir"].isin(EXCL_SEHIR)]
    oos = list(olay[olay.yil >= 2025].to_dict("records"))
    print(f"OOS olay (2025-26, izinli pistler): {len(oos)}")

    CFG = [("acgozlu900_bot2", 900, "bot2"), ("acgozlu900_bot1", 900, "bot1"),
           ("birlesim900", 900, "birlesim"),
           ("acgozlu1800_bot2", 1800, "bot2"), ("acgozlu1800_bot1", 1800, "bot1"),
           ("birlesim1800", 1800, "birlesim")]

    print("\n" + "=" * 108)
    print("BIRLESIM BACKTESTI — sadece 6/6 oder, birim 1,25 TL, ayni olaylar")
    print("=" * 108)
    print(f"{'config':>17} {'olay':>5} {'ort.kombo':>9} {'ayak isabet':>12} {'6/6':>4} {'5/6':>4} "
          f"{'maliyet':>11} {'getiri':>11} {'ROI%':>7} {'ROI %95 GA':>17} {'ort.temettu':>11}")
    S = {}
    for ad, mk, mod in CFG:
        r = calis(oos, pm2, pm1, wmap, mk, mod)
        S[ad] = r
        roi = (r["g6"].sum() - r["mal"].sum()) / r["mal"].sum() * 100
        lo, hi = boot_roi(r["mal"], r["g6"])
        print(f"{ad:>17} {len(r['mal']):>5} {r['mal'].sum()/len(r['mal'])/BIRIM:>9.0f} "
              f"%{100*r['ayak_tut']/r['ayak_top']:>10.1f} {r['a6']:>4} {r['a5']:>4} "
              f"{r['mal'].sum():>11,.0f} {r['g6'].sum():>11,.0f} {roi:>+7.1f} "
              f"[{lo:>+6.1f},{hi:>+6.1f}] {(np.mean(r['div']) if r['div'] else 0):>11,.0f}")

    print("\n" + "=" * 108)
    print("KARAR KRITERI (onceden baglandi): birlesim1800, 1800'luk IKI kontrolun ikisinden de")
    print("hem ayak isabetinde hem 6/6'da dusuk OLMAMALI.")
    print("=" * 108)
    b = S["birlesim1800"]
    gecti = True
    for ktrl in ("acgozlu1800_bot2", "acgozlu1800_bot1"):
        k = S[ktrl]
        i_b = b["ayak_tut"] / b["ayak_top"]; i_k = k["ayak_tut"] / k["ayak_top"]
        ok1 = i_b >= i_k; ok2 = b["a6"] >= k["a6"]
        gecti = gecti and ok1 and ok2
        x, y, pv, n = mcnemar(b["av"], k["av"])
        print(f"  vs {ktrl:>17}: ayak %{100*i_b:.1f} vs %{100*i_k:.1f} [{'OK' if ok1 else 'KALDI'}]"
              f"   6/6 {b['a6']} vs {k['a6']} [{'OK' if ok2 else 'KALDI'}]"
              f"   | esli: yalniz-birlesim {x}, yalniz-kontrol {y}, p={pv:.4f} ({n} ayak)")
    print(f"\n  SONUC: {'KRITER GECILDI -> canliya birlesim1800 eklenebilir' if gecti else 'KRITER GECILEMEDI -> canliya ALINMAZ'}")

    print("\nEK OKUMA (bilgi): birlesim900 vs 900'luk ebeveynler — mekanizmanin esit-butce etkisi")
    b9 = S["birlesim900"]
    for ktrl in ("acgozlu900_bot2", "acgozlu900_bot1"):
        k = S[ktrl]
        x, y, pv, n = mcnemar(b9["av"], k["av"])
        print(f"  vs {ktrl}: ayak %{100*b9['ayak_tut']/b9['ayak_top']:.1f} vs "
              f"%{100*k['ayak_tut']/k['ayak_top']:.1f}  6/6 {b9['a6']} vs {k['a6']}"
              f"  | yalniz-birlesim {x}, yalniz-kontrol {y}, p={pv:.4f}")


if __name__ == "__main__":
    main()
