# -*- coding: utf-8 -*-
"""
agf_harman.py — K129: AGF (Altılı havuzunun KENDİ fiyatı) üçüncü kaynak olarak. SALT-OKUNUR.

K74 Altılı havuzunda GERÇEK ve BÜYÜK bir yanlılık ölçtü — AGF payı %2'nin altındaki atlar
havuzun dediğinin **2,73 katı** kazanıyor; ganyanın AGF'den çok daha şanslı gördüğü atlarda
oran **3,40**. Ve K74 şunu yazıp bırakmıştı:

    "SIRADAKI SOMUT ADIM (henuz yapilmadi): kupon secimini bot2 yerine (kamu - AGF)
     ayrismasi ile agirliklandir -> gercek temettulerle backtest."

O adım 55 karar boyunca atılmadı. Bu betik onu, projenin KENDİ mimarisiyle atıyor:
Bot2 zaten `softmax(α·ln bot1 + γ·ln kamu)`. AGF üçüncü bir görüştür → doğal soru:
**`softmax(α·ln bot1 + γ·ln kamu + δ·ln agf)` içinde δ sıfırdan farklı mı?**

Bu, "(kamu−AGF) ile ağırlıklandır" fikrinin ölçülebilir ve aşırı-uydurmaya kapalı hâlidir:
δ elle seçilmez, 2024'te fit edilir; sıfır çıkarsa AGF'nin taşıdığı bilgi zaten bot2'de vardır.

=====================================================================================
ÖN-KAYITLI ÖLÇÜT — SONUÇLAR GÖRÜLMEDEN YAZILDI VE GİT'E MÜHÜRLENDİ (K33/K52)
=====================================================================================
0) MUTLAK SINIR: hiçbir dosyaya yazılmaz. `altili_backtest.py`, `model.py`, `ozellik.py`,
   `gunluk.py`, config'ler, KUPONLAR — hiçbiri değişmez. Kullanıcı "mevcut kuponlarımıza
   şimdilik dokunmasın" dedi; dokunulmuyor. Bir varyant kazansa bile canlıya ALINMAZ.

1) SIZINTI BEYANI (K111 Z2 mantığı): arşivdeki `agf1` **RESMÎ/SON** AGF'dir (feed'de
   RESMI=true, AGFMODTIME ~son). Kupon ise ayak 1'den önce kurulur. Yani bu ölçüm
   **İYİMSER ÜST SINIRDIR.** Canlıda zaman damgalı AGF var (`oran_log.agf1`), ama tarihsel
   kayıt son hâli. **Bu iyimser sürüm bile geçemezse, kol EVLEVİYETLE kapanır.**

2) KAPSAM: AGF'si dolu koşular. AGF koşu içinde normalize edilir (bir koşu iki Altılı'nın
   ayağıysa arşivde toplam 200 çıkıyor → payı kendi toplamına bölerek düzelt).

3) Y0 — KALİBRASYON KAPISI (asıl kapı):
   Üçlü harman `softmax(α·ln bot1 + γ·ln kamu + δ·ln agf)`, katsayılar 2024'te fit,
   test 2025-26. Kıyas: mevcut ikili harman `softmax(α·ln bot1 + γ·ln kamu)`, AYNI koşularda.
     GEÇER  ancak: (a) δ'nın %95 GA'sı sıfırı DIŞLIYOR **ve**
                   (b) üçlü harmanın OOS log-loss'u ikiliden DÜŞÜK **ve**
                   (c) (b)'deki farkın koşu-düzeyi eşleşmiş %95 GA'sı tamamen sıfırın altında.
     DÜŞERSE: AGF kolu KAPANIR. K74'ün sinyali gerçektir ama bot2'de zaten vardır.
   δ için GA: koşu-düzeyi bootstrap ile yeniden fit (500 tekrar).

4) Y1 — KUPON (YALNIZ Y0 geçerse çalıştırılır):
   Üçlü olasılık mevcut `kapsam` dağıtıcısına (K52) verilir, gerçek temettülerle 2025-26
   backtest; kıyas aynı olaylarda ikili olasılık. Ölçüt: eşleşmiş ROI farkı, olay-bootstrap
   %95 GA sıfırın üstünde olmalı. Aksi halde kol kapanır.
   Y0 düşerse Y1 **HİÇ ÇALIŞTIRILMAZ** (kapı geçilmeden para ölçümü yapmak, gürültüde
   arama demektir — K107'nin dersi).

5) TEŞHİS (hüküm ÜRETMEZ): K74'ün (1) ve (4) numaralı tabloları YALNIZ 2025-26'da yeniden
   üretilir. K74 tüm yıllara bakmıştı; sinyalin OOS'ta hâlâ durup durmadığı ayrı bir sorudur
   ve tabloyu görmek Y0'ın sonucunu yorumlamaya yarar.
=====================================================================================
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from model import race_struct, seg_softmax, logloss                 # noqa: E402

BOOT_KOSU = 4000
BOOT_DELTA = 500
RNG = np.random.default_rng(20260827)
EPS = 1e-12


def fit_blend(X, start, sizes, win):
    def negll(b):
        p = seg_softmax(X @ b, start, sizes)
        ll = np.log(p[win] + EPS).sum()
        grad = X[win].sum(0) - (X * p[:, None]).sum(0)
        return -ll, -grad
    return minimize(negll, np.zeros(X.shape[1]), jac=True, method="L-BFGS-B").x


def veri():
    o = pd.read_csv(KOK / "veri" / "altili_olasilik_bot1.csv", low_memory=False)
    k = pd.read_csv(KOK / "veri" / "katilim.csv",
                    usecols=["race_kod", "tarih", "no", "agf1"], low_memory=False)
    k["agf1"] = pd.to_numeric(k["agf1"], errors="coerce")
    k["no"] = pd.to_numeric(k["no"], errors="coerce")
    o["no"] = pd.to_numeric(o["no"], errors="coerce")
    d = o.merge(k, on=["race_kod", "no"], how="inner")
    d["yil"] = pd.to_datetime(d["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    d = d.dropna(subset=["agf1", "bot1", "bot2", "kamu", "yil"])
    # AGF'yi kosu ICINDE normalize et (bir kosu iki Altili'nin ayagiysa toplam 200 cikiyor)
    s = d.groupby("race_kod")["agf1"].transform("sum")
    d = d[s > 0].copy()
    d["agf_p"] = d["agf1"] / d.groupby("race_kod")["agf1"].transform("sum")
    # tek galipli, >=4 atli
    gw = d.groupby("race_kod")["kazandi"].transform("sum")
    sz = d.groupby("race_kod")["race_kod"].transform("size")
    d = d[(gw == 1) & (sz >= 4)].sort_values(["race_kod", "no"]).reset_index(drop=True)
    d["agf_p"] = d["agf_p"].clip(lower=1e-6)
    return d


def kur(df, kolonlar):
    st, sz, win = race_struct(df)
    X = np.column_stack([np.log(df[c].to_numpy(float) + EPS) for c in kolonlar])
    return X, st, sz, win


def main():
    print("=" * 104)
    print("K129 — AGF ÜÇÜNCÜ KAYNAK OLARAK (K74'ün yapılmamış adımı). SALT-OKUNUR.")
    print("Ölçüt betiğin başında ÖN-KAYITLI. SIZINTI: arşivdeki AGF SON hâli -> İYİMSER ÜST SINIR.")
    print("=" * 104)
    d = veri()
    va = d[d.yil == 2024].reset_index(drop=True)
    te = d[d.yil >= 2025].reset_index(drop=True)
    print(f"  AGF'li koşu — val(2024): {va.race_kod.nunique():,} · "
          f"test(2025-26): {te.race_kod.nunique():,}")
    if te.race_kod.nunique() < 300 or va.race_kod.nunique() < 300:
        print("  YETERSİZ ÖRNEKLEM -> hüküm yok.")
        return

    # ---------------------- TESHIS: K74 tablolari, YALNIZ 2025-26 ---------------------
    print("\n" + "-" * 104)
    print("  TEŞHİS (hüküm üretmez) — K74'ün tabloları YALNIZ 2025-26'da")
    print("-" * 104)
    t = te.copy()
    t["kova"] = pd.cut(t["agf_p"], [0, .02, .05, .15, .30, .45, 1.01],
                       labels=["≤%2", "%2-5", "%5-15", "%15-30", "%30-45", ">%45"])
    g = t.groupby("kova", observed=True).agg(nat=("kazandi", "size"), AGF=("agf_p", "mean"),
                                             GERCEK=("kazandi", "mean"))
    g["oran"] = g["GERCEK"] / g["AGF"]
    print(f"  {'AGF payı':>10} {'at':>8} {'AGF':>8} {'GERÇEK':>8} {'oran':>7}")
    for i, r in g.iterrows():
        print(f"  {str(i):>10} {int(r.nat):>8,} {100*r.AGF:>7.2f}% {100*r.GERCEK:>7.2f}% "
              f"{r.oran:>7.2f}")
    t["fark"] = t["kamu"] - t["agf_p"]
    t["fk"] = pd.cut(t["fark"], [-1.01, -.10, -.05, .05, .10, 1.01],
                     labels=["<−0,10", "−0,10..−0,05", "~0", "+0,05..0,10", ">+0,10"])
    g2 = t.groupby("fk", observed=True).agg(nat=("kazandi", "size"), AGF=("agf_p", "mean"),
                                            kamu=("kamu", "mean"), GERCEK=("kazandi", "mean"))
    g2["AGF_orani"] = g2["GERCEK"] / g2["AGF"]
    print(f"\n  {'kamu − AGF':>14} {'at':>8} {'AGF':>8} {'kamu':>8} {'GERÇEK':>8} {'AGF oranı':>10}")
    for i, r in g2.iterrows():
        print(f"  {str(i):>14} {int(r.nat):>8,} {100*r.AGF:>7.2f}% {100*r.kamu:>7.2f}% "
              f"{100*r.GERCEK:>7.2f}% {r.AGF_orani:>10.2f}")

    # ------------------------------ Y0: KALIBRASYON KAPISI ---------------------------
    print("\n" + "=" * 104)
    print("Y0 — KALİBRASYON KAPISI (ölçüt 3)")
    print("=" * 104)
    Xv2, stv, szv, winv = kur(va, ["bot1", "kamu"])
    Xv3, _, _, _ = kur(va, ["bot1", "kamu", "agf_p"])
    b2 = fit_blend(Xv2, stv, szv, winv)
    b3 = fit_blend(Xv3, stv, szv, winv)
    print(f"  ikili harman (2024 fit): alpha={b2[0]:+.3f}  gamma={b2[1]:+.3f}")
    print(f"  üçlü harman  (2024 fit): alpha={b3[0]:+.3f}  gamma={b3[1]:+.3f}  "
          f"**delta(AGF)={b3[2]:+.3f}**")

    # delta GA — kosu duzeyi bootstrap, yeniden fit
    kosu_idx = np.arange(len(stv))
    ds = []
    for _ in range(BOOT_DELTA):
        pick = RNG.integers(0, len(stv), len(stv))
        satir = np.concatenate([np.arange(stv[i], stv[i] + szv[i]) for i in pick])
        yeni_sz = szv[pick]
        yeni_st = np.r_[0, np.cumsum(yeni_sz)[:-1]]
        try:
            bb = fit_blend(Xv3[satir], yeni_st, yeni_sz, winv[satir])
            ds.append(bb[2])
        except Exception:                                        # noqa: BLE001
            pass
    ds = np.array(ds)
    dlo, dhi = np.percentile(ds, 2.5), np.percentile(ds, 97.5)
    a_ok = not (dlo <= 0 <= dhi)
    print(f"  delta %95 GA [{dlo:+.3f} .. {dhi:+.3f}]  -> sıfırı "
          f"{'DIŞLIYOR' if a_ok else 'İÇERİYOR'}  (şart a: {'TAMAM' if a_ok else 'DÜŞTÜ'})")

    Xt2, stt, szt, wint = kur(te, ["bot1", "kamu"])
    Xt3, _, _, _ = kur(te, ["bot1", "kamu", "agf_p"])
    p2 = seg_softmax(Xt2 @ b2, stt, szt)
    p3 = seg_softmax(Xt3 @ b3, stt, szt)
    ll2, ll3 = logloss(p2, stt, szt, wint), logloss(p3, stt, szt, wint)
    # referans: AGF'nin kendisi ve kamu'nun kendisi
    lla = logloss(te["agf_p"].to_numpy(float), stt, szt, wint)
    llk = logloss(te["kamu"].to_numpy(float), stt, szt, wint)
    print(f"\n  OOS (2025-26) log-loss — düşük iyi:")
    print(f"     yalnız AGF        : {lla:.4f}")
    print(f"     yalnız kamu       : {llk:.4f}")
    print(f"     ikili harman      : {ll2:.4f}")
    print(f"     ÜÇLÜ harman (+AGF): {ll3:.4f}   fark {ll3-ll2:+.4f}")
    b_ok = ll3 < ll2
    print(f"     (şart b: {'TAMAM' if b_ok else 'DÜŞTÜ'})")

    k2 = -np.log(p2[wint] + EPS)
    k3 = -np.log(p3[wint] + EPS)
    fark = k3 - k2
    idx = RNG.integers(0, len(fark), size=(BOOT_KOSU, len(fark)))
    bb = fark[idx].mean(axis=1)
    lo, hi = np.percentile(bb, 2.5), np.percentile(bb, 97.5)
    c_ok = hi < 0
    print(f"     eşleşmiş fark %95 GA [{lo:+.4f} .. {hi:+.4f}] -> "
          f"(şart c: {'TAMAM' if c_ok else 'DÜŞTÜ'})")

    print("\n" + "=" * 104)
    if a_ok and b_ok and c_ok:
        print("Y0 GEÇTİ -> Y1 (kupon backtest) çalıştırılabilir. Ölçüt 4.")
    else:
        eksik = [n for n, ok in (("a: delta≠0", a_ok), ("b: log-loss↓", b_ok),
                                 ("c: GA<0", c_ok)) if not ok]
        print(f"Y0 DÜŞTÜ ({' · '.join(eksik)}) -> **AGF KOLU KAPANIR.**")
        print("Y1 (kupon backtest) ÇALIŞTIRILMAZ (ölçüt 4: kapı geçilmeden para ölçmek")
        print("gürültüde aramaktır — K107'nin dersi).")
        print("Okuma: K74'ün sinyali GERÇEK ama bot2'nin taşıdığı bilginin ÜSTÜNE bir şey")
        print("koymuyor. Üstelik bu ölçüm İYİMSER (son AGF kullanıldı) -> canlıda daha kötü.")
    print("=" * 104)


if __name__ == "__main__":
    main()
