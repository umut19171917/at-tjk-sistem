# -*- coding: utf-8 -*-
"""
zamanlama_onkayit.py — BEKLEYENLER #4'ün CANLI KOL SINAMASI (K105/K106'da bağlanan tetik).
SALT-OKUNUR: hiçbir dosyaya yazmaz, canlıya dokunmaz.

=====================================================================================
TETİK ve ÖLÇÜM — K105(g)/K106'da, sonuç görülmeden yazıldı:
  "`orta_15` ~60 kupona ulaşınca → EŞLEŞMİŞ AYAK KIYASI (aynı Altılı, iki zaman)
   + simülasyonla karşılaştır. Canlı zamanlama o güne kadar 30 dk KALIR."
  Simülasyon önseli (K105-b, 18 Altılı/108 ayak): orta **+5 ayak, p=0,424** ·
  genis900 +4 · bot1 **+0** (iç kontrol).
=====================================================================================

TASARIM. İki canlı çift var; her çiftin TEK farkı kupon kurulma anıdır:
    orta (30 dk)        ↔ orta_15 (15 dk)          — DAR kupon (96 kombo)
    acgozlu900 (30 dk)  ↔ acgozlu900_15 (15 dk)    — GENİŞ kupon (900 kombo)
Kıyas AYNI Altılı'nın AYNI ayağında yapılır → pist, saha, hava, bütçe, dağıtıcı ve kesinti
denklemden düşer. #11 (İstanbul) bu tasarımda zaten sadeleşir; 7 Eyl'de düşmesi endişeyi
büsbütün kaldırdı.

İÇ KONTROL (yöntemin kendini sınaması). İki kol AYNI atları yazdığı ayaklarda sonuç
ZORUNLU olarak aynıdır. Orada tek bir uyumsuzluk çıkarsa eşleştirme bozuktur ve hiçbir
sayı okunmaz. Uyumsuz çiftler YALNIZCA seçim gerçekten değiştiği ayaklardan gelmelidir.

İSTATİSTİK: McNemar (tam binom, eşleşmiş) + olay düzeyi bootstrap (aynı Altılı'nın 6 ayağı
bağımsız değil). Ayrıca 6/6 ve para — K111'in dersi: isabet ile para AYNI yöne gitmeyebilir.
"""
import sys
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
import rapor_ortak as ro                                            # noqa: E402

CIFTLER = [("orta", "orta_15", "DAR (96 kombo)", +5),
           ("acgozlu900", "acgozlu900_15", "GENİŞ (900 kombo)", +4)]
TEKRAR = 10000
TOHUM = 20260907


def mcnemar_p(a, b):
    """Tam iki yanlı binom (p=0,5). a,b = uyumsuz çiftlerin iki yönü."""
    n = a + b
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(comb(n, i) for i in range(min(a, b) + 1)) / 2 ** n)


def main():
    k = pd.read_csv(KOK / "veri" / "altili_kupon.csv", low_memory=False)
    k = k[k["tuttu"].notna()].copy()
    k["tuttu"] = k["tuttu"].astype(int)
    t = pd.read_csv(KOK / "veri" / "altili_temettu.csv")
    tem = {(r.tarih, r.pist, int(r.seq)): float(r.temettu)
           for r in t.itertuples() if pd.notna(r.temettu)}

    print("=" * 100)
    print("BEKLEYENLER #4 — ZAMANLAMA (30 dk vs 15 dk): CANLI KOLUN EŞLEŞMİŞ SINAMASI")
    print("=" * 100)

    for c30, c15, etiket, sim in CIFTLER:
        a = k[k.config == c30].set_index(["tarih", "pist", "seq", "ayak"])
        b = k[k.config == c15].set_index(["tarih", "pist", "seq", "ayak"])
        ortak = a.index.intersection(b.index)
        A, B = a.loc[ortak], b.loc[ortak]

        kupon15 = k[k.config == c15].groupby(["tarih", "pist", "seq"]).ngroups
        print("\n" + "=" * 100)
        print(f"  {c30}  ↔  {c15}   —   {etiket}")
        print("=" * 100)
        print(f"  tetik      : {kupon15} kupon / 60 "
              f"{'✓ DOLU' if kupon15 >= 60 else '✗ dolmadı — DUR'}")
        if kupon15 < 60:
            continue
        print(f"  eşleşen ayak: {len(ortak):,}  "
              f"({A.index.droplevel(3).nunique()} Altılı olayı)")

        # ------------------------------------------------------- iç kontrol
        ayni_secim = (A["secim"].astype(str).values == B["secim"].astype(str).values)
        ayni_sonuc = (A["tuttu"].values == B["tuttu"].values)
        ihlal = int((ayni_secim & ~ayni_sonuc).sum())
        print(f"  İÇ KONTROL : aynı seçim yazılan ayak {int(ayni_secim.sum()):,}/{len(ortak):,}"
              f"  ({100*ayni_secim.mean():.1f}%) · bunlarda sonuç uyumsuzluğu {ihlal}"
              f"  {'✓ temiz' if ihlal == 0 else '*** YÖNTEM BOZUK — OKUMA ***'}")
        if ihlal:
            continue
        # genislik esitligi de dogrulanmali (K105: cift kurulurken dogrulandi)
        gen = int((A["nat"].values != B["nat"].values).sum())
        print(f"               genişlik (nat) farklı olan ayak: {gen}"
              f"  {'✓ genişlik sabit' if gen == 0 else '(dağıtıcı genişliği kaydırmış)'}")

        # ------------------------------------------------------- McNemar
        y30 = A["tuttu"].values.astype(bool)
        y15 = B["tuttu"].values.astype(bool)
        n10 = int((y30 & ~y15).sum())          # yalnız 30 dk tuttu
        n01 = int((~y30 & y15).sum())          # yalnız 15 dk tuttu
        p = mcnemar_p(n10, n01)
        print(f"\n  ayak isabeti : 30 dk %{100*y30.mean():.1f}   15 dk %{100*y15.mean():.1f}"
              f"   fark {100*(y15.mean()-y30.mean()):+.2f} puan")
        print(f"  uyumsuz çift : yalnız 30 dk {n10} · yalnız 15 dk {n01}"
              f"  → net {n01-n10:+d} ayak · McNemar p={p:.3f}")
        print(f"  simülasyon önseli (K105-b): {sim:+d} ayak / 108 ayak = "
              f"{100*sim/108:+.2f} puan (p=0,424)")

        # --------------------------------------------- GENİŞLİK ARTEFAKTI AYIKLAMASI
        # Açgözlü dağıtıcı bütçeyi olasılığa göre paylaştırır: olasılık değişince GENİŞLİK
        # de kayar. O zaman "+n ayak" zamanlamadan mı, yoksa o ayakta tesadüfen daha çok at
        # yazmış olmaktan mı geliyor ayırt edilemez. Ayıklama: genişliği BİREBİR aynı olan
        # ayaklarda testi tekrarla — orada zamanlama TEK değişkendir.
        m = (A["nat"].values == B["nat"].values)
        g10 = int((y30 & ~y15 & m).sum())
        g01 = int((~y30 & y15 & m).sum())
        print(f"  ── genişlik ARTEFAKTI ayıklaması ──")
        print(f"     15 dk daha GENİŞ {int((B['nat'].values > A['nat'].values).sum())} ayak · "
              f"daha DAR {int((B['nat'].values < A['nat'].values).sum())} ayak")
        print(f"     YALNIZ eşit-genişlik ayaklarda ({int(m.sum())}): yalnız 30 dk {g10} · "
              f"yalnız 15 dk {g01} → net {g01-g10:+d} ayak · p={mcnemar_p(g10, g01):.3f}")
        print(f"     {'→ işaret eşit genişlikte de duruyor: zamanlama etkisi' if (g01-g10) * (n01-n10) > 0 else '→ *** İŞARET KAYBOLUYOR/TERSİNİYOR: net fark GENİŞLİK kaymasından ***'}")

        # ------------------------------------------------------- olay bootstrap
        olay = pd.MultiIndex.from_arrays(
            [A.index.get_level_values(i) for i in range(3)]).to_flat_index().to_numpy()
        birim = pd.DataFrame({"olay": olay, "d": y15.astype(int) - y30.astype(int)})
        grp = [g["d"].to_numpy() for _, g in birim.groupby("olay")]
        rng = np.random.default_rng(TOHUM)
        boot = np.empty(TEKRAR)
        for i in range(TEKRAR):
            s = rng.choice(len(grp), len(grp))
            boot[i] = 100 * np.concatenate([grp[j] for j in s]).mean()
        alt, ust = np.percentile(boot, [2.5, 97.5])
        print(f"  olay-bootstrap %95 GA: [{alt:+.2f}, {ust:+.2f}] puan"
              f"   → {'sıfırı DIŞLIYOR' if (alt > 0 or ust < 0) else 'sıfırı İÇERİYOR'}")

        # ------------------------------------------------------- kupon + para
        print(f"\n  {'kol':>14} {'kupon':>6} {'6/6':>4} {'5/6':>4} {'bedel':>11} "
              f"{'ödül':>11} {'net':>11} {'ROI':>8}")
        for ad, df in ((c30, A), (c15, B)):
            bedel = odul = 0.0
            kup = tam = bes = 0
            for key, g in df.groupby(level=[0, 1, 2]):
                if len(g) != 6:
                    continue
                kup += 1
                bedel += int(np.prod(g["nat"])) * ro.birim_fiyat(key[1])
                s = int(g["tuttu"].sum())
                if s == 6:
                    tam += 1
                    odul += tem.get((key[0], key[1], int(key[2])), 0.0)
                elif s == 5:
                    bes += 1
            roi = 100 * (odul - bedel) / bedel if bedel else np.nan
            print(f"  {ad:>14} {kup:>6} {tam:>4} {bes:>4} {bedel:>11,.0f} "
                  f"{odul:>11,.0f} {odul-bedel:>+11,.0f} {roi:>+7.1f}%")

    print("\n" + "=" * 100)
    print("  Okuma kuralı (K111): isabet ve para AYNI yöne gitmek zorunda değil.")
    print("  Hüküm için GA sıfırı dışlamalı; dışlamıyorsa 'işaret yok' denir, yön okunmaz.")
    print("=" * 100)


if __name__ == "__main__":
    main()
