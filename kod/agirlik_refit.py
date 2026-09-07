# -*- coding: utf-8 -*-
"""
agirlik_refit.py — BEKLEYENLER #6'nın ÖLÇÜT KODU. SALT-OKUNUR (canlı ağırlığa DOKUNMAZ).

=====================================================================================
BU DOSYA 7 EYLÜL 2026'DA YAZILDI VE GİT'E MÜHÜRLENDİ — ÖLÇÜM PENCERESİ 25 EYLÜL.
=====================================================================================
#6 tarih tetikli (25 Eyl) ve BEKLEYENLER'de yalnız şu yönerge vardı:
  "o gün aynı ölçüm tekrarlanıp K96'daki sayılarla KIYASLANMALI, SIFIRDAN hesaplanmamalı."
Yani YÖNTEM belliydi ama GEÇME EŞİĞİ yazılmamıştı. Bu dosya eşiği, veri görülmeden koyar.

CANLI KURULUM (koddan doğrulandı, gunluk.egit_ve_uygula):
  Bot1  : oran-kör conditional logit, eğitim  yıl <= 2024
  Bot2  : harman (alpha,gamma), eğitim  yıl == 2025
  Ağırlıklar HER GÜN yeniden fit edilir ama PENCERE donuktur; #6'nın sorusu pencereyi
  ileri kaydırmak, katsayıyı elle değiştirmek değil.

=====================================================================================
ÖN-KAYITLI ÖLÇÜT — 7 Eyl 2026, çıktı görülmeden:

  KONTROL (A) : Bot1 <= 2024 · harman 2025            [canlıda olan]
  KOL     (B) : Bot1 <= 2024 · harman 2025 + 2026-H1  [harman penceresi ileri]
  KOL     (C) : Bot1 <= 2025 · harman 2026-H1         [bot1 penceresi de ileri]

  SINAV KÜMESİ: 2026-07-01 .. çalıştırma günü. Üç kolun HİÇBİRİ bu aralıkta eğitilmez.
                Bu aralık kupon akışının da başladığı dönemdir (20 Tem) — yani ölçüm,
                sistemin canlı çalıştığı gerçek pencerede yapılır.
  ÖLÇÜ        : koşu başına ortalama log-olabilirlik, log p(gerçek galip). K96 ile AYNI ölçü.
  İSTATİSTİK  : delta = LL(kol) − LL(A), KOŞU düzeyi bootstrap, 10.000 tekrar.
  ÇOKLULUK    : iki kol aynı kontrole karşı sınanıyor -> Bonferroni. Eşik %95 değil,
                **%97,5 çift yanlı GA** (yani [1,25 , 98,75] yüzdelikleri).
  DEĞİŞTİR    : canlı pencere ANCAK bir kolun GA'sının ALT ucu > 0 ise ileri kaydırılır.
  DEĞİŞTİRME  : aksi hâlde pencere AYNEN kalır ve madde kapanır.

  BEKLENTİ (önceden yazılıyor): DEĞİŞMEYECEK. K96 aynı ölçümü 2.513 koşuda yaptı,
  fark +0,00014 ve %95 GA sıfırı içeriyordu. Bu ölçüm onu daha uzun pencerede tekrarlar.

  ÖDÜNÇ (K38/#6'da zaten yazılı): pencere ileri kaydırılırsa o dönem EĞİTİME döner ve
  temiz OOS biter -> yeni bir sınav dönemi tanımlamak GEREKİR. Bu, "geçerse otomatik yap"
  değil; geçerse KULLANICIYA bu ödünçle birlikte sunulur.

  BİLİNEN KİRLİLİK (K130) — ölçütün parçası olarak beyan: `ganyan_muhtemel` arşivde
  `ganyan_kapanis`in kopyası. Piyasa terimi hem eğitimde hem sınavda bu sütundan geliyor,
  yani ÜÇ KOL DA AYNI ölçüde etkileniyor -> KIYAS adil, SEVİYE değil. Bu ölçümden çıkan
  hüküm "hangi pencere daha iyi" sorusuna geçerlidir; "model ne kadar iyi" sorusuna değil.
  KOR DUMAN TESTI (kayda geciyor): 7 Eyl 2026'da bu betik `--zorla` ile BIR KEZ kosturuldu,
  ama cikti `/dev/null`a yonlendirildi ve YALNIZ cikis kodu (0) ile stderr (bos) okundu.
  Amac: 25 Eylul'de kodun cokmeyecegini dogrulamak. Sonuc GORULMEDI; muhur bozulmadi.
  `--zorla` bayragi kasten duruyor ki bu testin nasil yapildigi tekrarlanabilir olsun.
=====================================================================================
"""
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from model import FEAT, fit_clogit, seg_softmax, devig                # noqa: E402

KARAR_GUNU = date(2026, 9, 25)
SINAV_BAS = "2026-07-01"
H1_SON = "2026-06-30"
TEKRAR = 10000
TOHUM = 20260925
YUZDELIK = [1.25, 98.75]          # Bonferroni: iki kol -> %97,5 cift yanli


def race_struct(d):
    sz = d.groupby("race_kod", sort=False)["race_kod"].size().values
    st = np.r_[0, np.cumsum(sz)[:-1]]
    win = d["kazandi"].values.astype(bool)
    return st, sz, win


def hazirla():
    d = pd.read_csv(KOK / "veri" / "ozellikli.csv", low_memory=False)
    d["dt"] = pd.to_datetime(d["tarih"], errors="coerce")
    d = d[d["dt"].notna()]
    d = d[~d["kosmaz_b"].fillna(0).astype(bool)] if "kosmaz_b" in d else d
    for c in FEAT + ["ganyan_muhtemel", "kazandi"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d[FEAT] = d[FEAT].fillna(0.0)
    d = d[d["ganyan_muhtemel"] > 1]
    gw = d.groupby("race_kod")["kazandi"].transform("sum")
    sz = d.groupby("race_kod")["race_kod"].transform("size")
    d = d[(gw == 1) & (sz >= 4)]
    return d.sort_values(["race_kod", "no"]).reset_index(drop=True)


def kol(d, bot1_son, harman_bas, harman_son, sinav):
    """Bir kolu eğitip SINAV kümesinde koşu başına log-olabilirlik döndürür."""
    tr = d[d["dt"] <= pd.Timestamp(bot1_son)].sort_values("race_kod").reset_index(drop=True)
    beta = fit_clogit(tr[FEAT].values, *race_struct(tr))

    va = d[(d["dt"] >= pd.Timestamp(harman_bas)) & (d["dt"] <= pd.Timestamp(harman_son))]
    va = va.sort_values("race_kod").reset_index(drop=True)
    stv, szv, winv = race_struct(va)
    pfv = seg_softmax(va[FEAT].values @ beta, stv, szv)
    pmv = devig(va["ganyan_muhtemel"].values, stv, szv)
    alpha, gamma = fit_clogit(np.c_[np.log(pfv + 1e-12), np.log(pmv + 1e-12)], stv, szv, winv)

    st, sz, win = race_struct(sinav)
    pf = seg_softmax(sinav[FEAT].values @ beta, st, sz)
    pm = devig(sinav["ganyan_muhtemel"].values, st, sz)
    p = seg_softmax(alpha * np.log(pf + 1e-12) + gamma * np.log(pm + 1e-12), st, sz)
    return np.log(p[win] + 1e-12), float(alpha), float(gamma), va["race_kod"].nunique()


def main(argv):
    bugun = date.today()
    print("=" * 100)
    print("BEKLEYENLER #6 — MODEL AGIRLIK PENCERESI ILERI KAYDIRILMALI MI?")
    print("=" * 100)
    if bugun < KARAR_GUNU and "--zorla" not in argv:
        print(f"  MUHUR ACIK DEGIL. Olcum gunu {KARAR_GUNU:%d %b %Y}, bugun {bugun:%d %b %Y} "
              f"({(KARAR_GUNU-bugun).days} gun var).")
        print("  Bu betik 7 Eyl 2026'da yazilip git'e muhurlendi; ERKEN BAKMAK on-kaydi bozar.")
        return 2

    d = hazirla()
    sinav = d[d["dt"] >= pd.Timestamp(SINAV_BAS)].sort_values("race_kod").reset_index(drop=True)
    print(f"  sinav kumesi : {SINAV_BAS} .. {bugun:%Y-%m-%d}  ->  "
          f"{sinav['race_kod'].nunique():,} kosu  (hicbir kol burada egitilmedi)")
    print(f"  esik         : Bonferroni %97,5 cift yanli GA (iki kol, tek kontrol)\n")

    kollar = [("A  KONTROL (canlida olan)", "2024-12-31", "2025-01-01", "2025-12-31"),
              ("B  harman penceresi ileri", "2024-12-31", "2025-01-01", H1_SON),
              ("C  bot1 penceresi de ileri", "2025-12-31", "2026-01-01", H1_SON)]
    sonuc = {}
    for ad, b1, hb, hs in kollar:
        ll, a, g, n = kol(d, b1, hb, hs, sinav)
        sonuc[ad[0]] = ll
        print(f"  {ad:<28} alpha={a:+.3f} gamma={g:+.3f}  harman {n:,} kosu  "
              f"LL/kosu {ll.mean():+.4f}")

    rng = np.random.default_rng(TOHUM)
    print("\n" + "-" * 100)
    print("  KIYAS (kontrole karsi, koşu duzeyi bootstrap)")
    print("-" * 100)
    degistir = []
    for k in ("B", "C"):
        fark = sonuc[k] - sonuc["A"]
        boot = np.empty(TEKRAR)
        for i in range(TEKRAR):
            boot[i] = fark[rng.integers(0, len(fark), len(fark))].mean()
        alt, ust = np.percentile(boot, YUZDELIK)
        ok = alt > 0
        degistir.append(ok)
        print(f"  {k} - A : delta LL/kosu {fark.mean():+.5f}   %97,5 GA [{alt:+.5f}, {ust:+.5f}]"
              f"   {'GECTI' if ok else 'gecmedi'}")
    print(f"\n  K96 referansi (7 Agu 2026, 2.513 kosu): yeniden-fit farki +0,00014, "
          f"%95 GA sifiri iceriyordu.")

    print("\n" + "=" * 100)
    if any(degistir):
        print("  HUKUM: bir kol esigi GECTI -> pencere ileri kaydirilabilir.")
        print("  ANCAK OTOMATIK YAPILMAZ: bu, sinav donemini EGITIME cevirir ve temiz OOS'u")
        print("  bitirir (K38/#6 odunc notu). Yeni bir sinav donemi tanimlanmadan uygulanmaz;")
        print("  karar KULLANICININ.")
    else:
        print("  HUKUM: hicbir kol esigi gecmedi -> CANLI PENCERE AYNEN KALIR, #6 KAPANIR.")
        print("  K96'nin 'yeniden fit gereksiz' erken cevabi daha uzun pencerede dogrulanmis olur.")
    print("=" * 100)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
