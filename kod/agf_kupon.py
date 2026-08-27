# -*- coding: utf-8 -*-
"""
agf_kupon.py — K129 / Y1: AGF'li üçlü olasılık KUPONA çevrilince ne oluyor? SALT-OKUNUR.

K129'un Y0 kapısı GEÇTİ: `softmax(α·ln bot1 + γ·ln kamu + δ·ln agf)` içinde δ=+0,586
(%95 GA [+0,483..+0,720]) ve OOS log-loss 1,7510 -> 1,7296 (−0,0214, %95 GA
[−0,0258..−0,0171]). Kıyas için: K128'in EN İYİ varyantı Bot2'yi −0,0006 oynatmıştı.
Bu 36 KAT daha büyük.

Ayrıca SIZINTI endişesi ÖLÇÜLDÜ ve neredeyse yok çıktı: canlı `altili_oran_log`'ta AGF
20-40 dk kala ile son hâli arasında **Spearman ρ = 0,9999** (ort. fark 0,05 puan); 120+ dk
kala bile ρ = 0,9983. Yani AGF kupon anında zaten elimizdedir. (Kıyas: ganyan oranı aynı
pencerede medyan +%12,7 kayıyor — K110.)

Geriye tek soru kaldı ve bu betik onu soruyor: **para kazandırıyor mu?**

=====================================================================================
ÖN-KAYITLI ÖLÇÜT (K129 madde 4'ün uygulaması; sonuçlar görülmeden yazıldı)
=====================================================================================
0) MUTLAK SINIR: hiçbir dosyaya yazılmaz. `altili_backtest.py` DEĞİŞTİRİLMEZ, yalnız
   import edilir. Config, dağıtıcı, canlı akış, KUPONLAR — hiçbiri değişmez.
   Kullanıcı "mevcut kuponlarımıza şimdilik dokunmasın" dedi. Dokunulmuyor.

1) TASARIM: aynı olaylar, aynı dağıtıcı (`kupon_kur` = K52 kapsam ailesi), aynı bütçe,
   aynı gerçek temettüler. TEK fark: ayak puanı
      ESKİ = bot2  (mevcut üretim)
      YENİ = üçlü harman (bot1 + kamu + AGF), katsayılar 2024'te fit
2) BAŞ HÜCRE (önceden seçildi): üretimin `orta` config'i — kapsam 0,75 · maxKombo 96 ·
   banker 0,70. Diğer hücreler YALNIZ duyarlılık olarak basılır, hüküm onlardan çıkmaz.
3) ÖLÇÜT: eşleşmiş ROI farkı (YENİ − ESKİ), olay-bootstrap %95 GA.
      GA'nın TAMAMI sıfırın üstünde -> **GEÇTİ**
      aksi halde                    -> **DÜŞTÜ, AGF kupon kolu KAPANIR**
4) İKİNCİ OKUMA (hüküm üretmez): 6/6 sayısı, ortalama temettü, ortalama kombo.
5) UYARI: 6/6 nadirdir; ROI tek bir büyük temettüyle savrulur (K122'nin dersi). Bu yüzden
   ROI farkının yanında **6/6 sayısı** ve **ayak isabeti** de raporlanır — ikincisi düşük
   varyanslı ve daha okunaklıdır.
6) KAPSAM: 2025-26 (gerçek OOS), izinli pist (EXCL), AGF'si TAM ve toplamı ~100 olan
   koşular. Eksik AGF'li koşu ATLANIR (normalizasyon artefaktını önler).
=====================================================================================
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from model import race_struct, seg_softmax                          # noqa: E402
import altili_backtest as AB                                        # noqa: E402

EPS = 1e-12
BOOT = 4000
RNG = np.random.default_rng(20260827)
BAS_KAPSAM, BAS_KOMBO, BAS_BANKER = 0.75, 96, 0.70


def fit_blend(X, st, sz, w):
    def f(b):
        p = seg_softmax(X @ b, st, sz)
        return -np.log(p[w] + EPS).sum(), -(X[w].sum(0) - (X * p[:, None]).sum(0))
    return minimize(f, np.zeros(X.shape[1]), jac=True, method="L-BFGS-B").x


def hazirla():
    o = pd.read_csv(KOK / "veri" / "altili_olasilik_bot1.csv", low_memory=False)
    k = pd.read_csv(KOK / "veri" / "katilim.csv",
                    usecols=["race_kod", "tarih", "no", "agf1", "kosmaz"], low_memory=False)
    k["agf1"] = pd.to_numeric(k["agf1"], errors="coerce")
    k["no"] = pd.to_numeric(k["no"], errors="coerce")
    o["no"] = pd.to_numeric(o["no"], errors="coerce")
    k = k[~k["kosmaz"].fillna(False).astype(bool)]
    d = o.merge(k, on=["race_kod", "no"], how="inner")
    d["yil"] = pd.to_datetime(d["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    # AGF TAM ve toplami ~100 olan kosular (olcut 6)
    g = d.groupby("race_kod").agg(n=("no", "size"), nagf=("agf1", lambda s: s.notna().sum()),
                                  top=("agf1", "sum"))
    iyi = set(g[(g.nagf == g.n) & (g.top.between(99, 101))].index)
    d = d[d.race_kod.isin(iyi)].copy()
    d["agf_p"] = (d["agf1"] / d.groupby("race_kod")["agf1"].transform("sum")).clip(lower=1e-6)
    gw = d.groupby("race_kod")["kazandi"].transform("sum")
    sz = d.groupby("race_kod")["race_kod"].transform("size")
    d = d[(gw == 1) & (sz >= 4)].sort_values(["race_kod", "no"]).reset_index(drop=True)
    return d


def main():
    print("=" * 100)
    print("K129 / Y1 — AGF'li üçlü olasılık KUPONA çevrildi. SALT-OKUNUR, canlıya dokunmaz.")
    print("=" * 100)
    d = hazirla()
    va = d[d.yil == 2024].reset_index(drop=True)
    print(f"  AGF'si TAM koşu — val(2024): {va.race_kod.nunique():,} · "
          f"tüm yıllar: {d.race_kod.nunique():,}")

    stv, szv, winv = race_struct(va)
    X3 = np.column_stack([np.log(va[c].to_numpy(float) + EPS) for c in ("bot1", "kamu", "agf_p")])
    b3 = fit_blend(X3, stv, szv, winv)
    print(f"  üçlü harman (2024 fit): alpha={b3[0]:+.3f} gamma={b3[1]:+.3f} delta={b3[2]:+.3f}")

    # her kosu icin ucuz olasilik (kosu ICINDE softmax — uretim deseni)
    puan_eski, puan_yeni, puan_full = {}, {}, {}
    for rk, g in d.groupby("race_kod", sort=False):
        g = g.sort_values("no")
        st, sz = np.array([0]), np.array([len(g)])
        s3 = (b3[0] * np.log(g["bot1"].to_numpy(float) + EPS)
              + b3[1] * np.log(g["kamu"].to_numpy(float) + EPS)
              + b3[2] * np.log(g["agf_p"].to_numpy(float) + EPS))
        p3 = seg_softmax(s3, st, sz)
        nos = g["no"].to_numpy()
        puan_eski[rk] = list(zip(nos, g["bot2"].to_numpy(float)))
        puan_yeni[rk] = list(zip(nos, p3))
        puan_full[rk] = list(zip(nos, g["bot2"].to_numpy(float), g["kazandi"].to_numpy()))

    olay = pd.read_csv(KOK / "veri" / "altili_tam.csv", low_memory=False)
    olay["yil"] = pd.to_datetime(olay["tarih"], format="%d/%m/%Y", errors="coerce").dt.year
    olay = olay[(~olay["sehir"].isin(AB.EXCL)) & (olay["yil"] >= 2025)]
    kayit = olay.to_dict("records")
    print(f"  2025-26 olay (izinli pist): {len(kayit):,}")

    def kos(pm, kapsam, kombo, banker):
        mal, get, alti, ayak = [], [], 0, []
        for o in kayit:
            r = AB.degerlendir(o, pm, puan_full, kapsam, kombo, banker, kademeli=False)
            if r is None:
                continue
            m, gt, a6 = r
            mal.append(m); get.append(gt); alti += a6
            legs = [int(o[f"leg{i+1}"]) for i in range(6)]
            sec = AB.kupon_kur([pm[x] for x in legs], kapsam, kombo, banker)
            kaz = [[n for n, p, kz in puan_full[x] if kz == 1][0] for x in legs]
            ayak.append(sum(kaz[i] in sec[i] for i in range(6)))
        return np.array(mal), np.array(get), alti, np.array(ayak)

    print("\n" + "-" * 100)
    print(f"  {'hücre':>22} {'oynanan':>8} {'ESKİ ROI':>9} {'YENİ ROI':>9} {'fark':>8} "
          f"{'6/6 E→Y':>9} {'ayak E→Y':>12}")
    print("-" * 100)
    bas = None
    for kapsam in (0.60, 0.75, 0.90):
        for kombo in (24, 96, 288):
            m1, g1, a1, y1 = kos(puan_eski, kapsam, kombo, BAS_BANKER)
            m2, g2, a2, y2 = kos(puan_yeni, kapsam, kombo, BAS_BANKER)
            n = min(len(m1), len(m2))
            r1 = (g1.sum() - m1.sum()) / m1.sum() * 100
            r2 = (g2.sum() - m2.sum()) / m2.sum() * 100
            isaret = " <-- BAŞ" if (kapsam == BAS_KAPSAM and kombo == BAS_KOMBO) else ""
            print(f"  {f'kapsam {kapsam} · K{kombo}':>22} {n:>8,} {r1:>+8.1f}% {r2:>+8.1f}% "
                  f"{r2-r1:>+7.1f} {f'{a1}→{a2}':>9} {f'{y1.mean():.3f}→{y2.mean():.3f}':>12}"
                  f"{isaret}")
            if kapsam == BAS_KAPSAM and kombo == BAS_KOMBO:
                bas = (m1, g1, m2, g2, a1, a2, y1, y2)

    m1, g1, m2, g2, a1, a2, y1, y2 = bas
    net1, net2 = g1 - m1, g2 - m2
    fark = net2 - net1
    idx = RNG.integers(0, len(fark), size=(BOOT, len(fark)))
    # ROI farki: bootstrap orneginde toplam net / toplam maliyet
    r1b = (net1[idx].sum(1) / m1[idx].sum(1)) * 100
    r2b = (net2[idx].sum(1) / m2[idx].sum(1)) * 100
    db = r2b - r1b
    lo, hi = np.percentile(db, 2.5), np.percentile(db, 97.5)

    print("\n" + "=" * 100)
    print("HÜKÜM (ön-kayıtlı ölçüt 3) — BAŞ HÜCRE: kapsam 0,75 · maxKombo 96 · banker 0,70")
    print("=" * 100)
    r1 = net1.sum() / m1.sum() * 100
    r2 = net2.sum() / m2.sum() * 100
    print(f"  ESKİ (bot2)        ROI {r1:+.1f}%   6/6: {a1}   ort. ayak isabeti {y1.mean():.3f}")
    print(f"  YENİ (bot1+kamu+AGF) ROI {r2:+.1f}%   6/6: {a2}   ort. ayak isabeti {y2.mean():.3f}")
    print(f"  FARK {r2-r1:+.1f} puan   %95 GA [{lo:+.1f} .. {hi:+.1f}]")
    if lo > 0:
        print("\n  -> GEÇTİ. AGF kupon seçimini ölçülebilir biçimde iyileştiriyor.")
    else:
        print("\n  -> DÜŞTÜ (GA sıfırı içeriyor ya da altında). **AGF KUPON KOLU KAPANIR.**")
    # dusuk varyansli ikinci okuma
    ay = y2 - y1
    ab = ay[RNG.integers(0, len(ay), size=(BOOT, len(ay)))].mean(1)
    print(f"\n  DÜŞÜK VARYANSLI OKUMA — ayak isabeti farkı: {ay.mean():+.4f} "
          f"ayak/kupon  %95 GA [{np.percentile(ab,2.5):+.4f} .. {np.percentile(ab,97.5):+.4f}]")
    print("  (6/6 nadirdir; ROI tek temettüyle savrulur — K122. Ayak isabeti daha okunaklı.)")
    print("\n  CANLIYA HİÇBİR ŞEY ALINMADI. KUPONLARA DOKUNULMADI (ölçüt 0).")


if __name__ == "__main__":
    main()
