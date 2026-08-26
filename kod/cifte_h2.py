# -*- coding: utf-8 -*-
"""
cifte_h2.py — K127: ÇİFTE kolunun İKİNCİ KAPISI (H2 — KENAR). SALT-OKUNUR / OFFLINE.

K125 kesintiyi %27,2 ölçüp kolu açtı. K126 (H1) havuzun kalibresiz olduğunu doğruladı
(Ç2−Ç3 = +17,8 puan, eşik +15). Geriye asıl soru kaldı:

   **Modelimizin ÇİFTE seçimi, KALABALIĞIN favorisini yeniyor mu?**

Yenmiyorsa ucuz kesintinin ve havuz yanlılığının hiçbir kıymeti yok: kalabalığın favorisini
oynamak zaten K126'da −%23,3 getiriyor. Kolun devamı yalnız modelin o −%23,3'ü kapatabilecek
kadar kalabalığı geçmesine bağlı.

=====================================================================================
ÖN-KAYITLI ÖLÇÜT — SONUÇLAR GÖRÜLMEDEN YAZILDI VE GİT'E MÜHÜRLENDİ (K33/K52)
=====================================================================================
1) KAPSAM: 2026 ÇİFTE fırsatları; HER İKİ AYAK da `veri/altili_olasilik_bot1.csv`'de
   olmalı (model kapsamı 2026'da 2.813/4.018 koşu).

2) EŞLEŞMİŞ KIYAS — aynı olaylar, aynı bedel (olay başına 1,00 TL, tek kombinasyon):
      M  (model) : her ayakta bot2'nin en yüksek olasılıklı atı
      K  (kamu)  : her ayakta kamu olasılığı en yüksek at (havuzun favorisi)
      B1 (bot1)  : her ayakta bot1'in en yüksek atı — oran-kör kol, YALNIZ BAĞLAM

3) BİRİNCİL ÖLÇÜT: M'nin ROI'si eksi K'nin ROI'si. Olay-bootstrap %90 GA, 2.000 tekrar.
      fark > 0 VE %90 GA'nın TAMAMI sıfırın üstünde  -> **H2 GEÇTİ**, kol H3'e (para) ilerler
      aksi halde                                      -> **H2 DÜŞTÜ, ÇİFTE KOLU KAPANIR**

4) GÜÇ KAPISI (K107): M ile K'nin FARKLI seçim yaptığı olay sayısı ("uyumsuz çift") **>= 6**
   olmalı. Altındaysa hüküm **"BAKILAMAZ"**: kol ne kapanır ne geçer, veri beklenir.
   (K106'nın A0 aşırı-yorumu bu kapıyla önlenmişti; aynısı burada da geçerli.)

5) İKİNCİ OKUMA (HÜKÜM ÜRETMEZ, yalnız bağlam): log-loss. p(çifte) = p(ayak1)·p(ayak2);
   kazanan çiftin olasılığının negatif logu. Model vs kamu, eşleşmiş, olay-bootstrap.

6) SIZINTI BEYANI (K97/K111): ayak 2'nin HEM model HEM kamu olasılıkları kapanış oranı
   türevlidir; kupon ise ayak 1'den önce alınır. Yani her iki kol da AYNI biçimde sızıntılı.
   -> ARALARINDAKİ FARK adildir (asıl ölçüt budur), ama MUTLAK ROI'ler oynanabilir DEĞİLDİR
   ve öyle raporlanır. Bu, K111'in Z2 mantığının aynısıdır.

7) KALİTE KAPISI: K126'nın kapısı aynen (beraberlik dışarıda, tek kazanan, kombinasyon
   gerçek kazananlarla doğrulanmış) + iki ayakta da model olasılığı dolu.

8) DOKUNULMAYANLAR: hiçbir dosyaya yazılmaz. Config, dağıtıcı, ağırlık, canlı akış — hiçbiri.
=====================================================================================
"""
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
import cifte_h1 as H1                                              # noqa: E402

BOOT = 2000
ASGARI_UYUMSUZ = 6
RNG = np.random.default_rng(20260827)


def model_tablosu():
    """race_kod -> {kolon: en yuksek olasilikli at no}."""
    o = pd.read_csv(KOK / "veri" / "altili_olasilik_bot1.csv", low_memory=False)
    for c in ("bot1", "bot2", "kamu"):
        o[c] = pd.to_numeric(o[c], errors="coerce")
    o["no"] = pd.to_numeric(o["no"], errors="coerce")
    o = o.dropna(subset=["no", "bot1", "bot2", "kamu"])
    T = {}
    for rk, g in o.groupby("race_kod"):
        nos = g["no"].to_numpy(int)
        T[int(rk)] = {c: int(nos[int(np.argmax(g[c].to_numpy(float)))])
                      for c in ("bot1", "bot2", "kamu")}
        T[int(rk)]["p"] = {c: dict(zip(nos, g[c].to_numpy(float)))
                           for c in ("bot2", "kamu")}
    return T


def boot(x):
    a = np.asarray(x, float)
    idx = RNG.integers(0, len(a), size=(BOOT, len(a)))
    return a[idx].mean(axis=1)


def main():
    print("=" * 100)
    print("K127 — ÇİFTE H2 KAPISI: model kalabalığı yeniyor mu? (2026, salt-okunur)")
    print("Ölçüt betiğin başında ÖN-KAYITLI. Sızıntı beyanı: madde 6.")
    print("=" * 100)

    T, kart = H1.kosular()
    F, _ = H1.firsatlar(T, kart)
    M = model_tablosu()

    # race_kod'u geri bul: H1.firsatlar sozluk donduruyor, race_kod tasimiyor -> yeniden esle
    kod = {}
    for rk, v in T.items():
        kod[(tuple(v["no"]), v["kazanan"], v["saha"])] = rk

    olay = []
    atilan = 0
    for A, B, d in F:
        ra = kod.get((tuple(A["no"]), A["kazanan"], A["saha"]))
        rb = kod.get((tuple(B["no"]), B["kazanan"], B["saha"]))
        if ra is None or rb is None or ra not in M or rb not in M:
            atilan += 1
            continue
        olay.append((M[ra], M[rb], A["kazanan"], B["kazanan"], d))
    print(f"  ÇİFTE fırsatı: {len(F):,} · model kapsamına giren: {len(olay):,} "
          f"(atılan {atilan:,})")
    if len(olay) < 200:
        print("  YETERSİZ ÖRNEKLEM -> hüküm yok.")
        return

    def getiri(kol):
        return np.array([d if (a[kol] == wa and b[kol] == wb) else 0.0
                         for a, b, wa, wb, d in olay])

    g = {k: getiri(k) for k in ("bot2", "kamu", "bot1")}
    print("\n" + "-" * 100)
    print(f"  {'kol':>34} {'isabet':>8} {'İADE':>9} {'ROI':>9} {'%90 GA (iade)':>19}")
    print("-" * 100)
    etiket = {"bot2": "M  model (bot2)", "kamu": "K  kalabalık favorisi",
              "bot1": "B1 bot1 (oran-kör, YALNIZ BAĞLAM)"}
    for k in ("bot2", "kamu", "bot1"):
        v = g[k]
        b = boot(v)
        print(f"  {etiket[k]:>34} {int((v>0).sum()):>8,} {100*v.mean():>8.1f}% "
              f"{100*v.mean()-100:>+8.1f}% "
              f"[{100*np.percentile(b,5):>7.1f} ..{100*np.percentile(b,95):>7.1f}]")

    # ------------------------------ GUC KAPISI (madde 4) --------------------------
    uyumsuz = sum(1 for a, b, wa, wb, d in olay
                  if (a["bot2"], b["bot2"]) != (a["kamu"], b["kamu"]))
    ayni = len(olay) - uyumsuz
    print(f"\n  GÜÇ KAPISI (madde 4): model ve kalabalık AYNI çifti seçiyor "
          f"{ayni:,}/{len(olay):,} olayda (%{100*ayni/len(olay):.1f}).")
    print(f"  Uyumsuz çift: {uyumsuz:,}  (asgari {ASGARI_UYUMSUZ})")

    fark = g["bot2"] - g["kamu"]
    fb = boot(fark)
    fo, flo, fhi = 100 * fark.mean(), 100 * np.percentile(fb, 5), 100 * np.percentile(fb, 95)

    print("\n" + "=" * 100)
    print("HÜKÜM (ön-kayıtlı madde 3-4)")
    print("=" * 100)
    print(f"  ÖLÇÜT = M ROI − K ROI = {fo:+.2f} puan   %90 GA [{flo:+.2f} .. {fhi:+.2f}]")
    if uyumsuz < ASGARI_UYUMSUZ:
        print(f"\n  -> BAKILAMAZ: uyumsuz çift {uyumsuz} < {ASGARI_UYUMSUZ}. "
              "Kol NE kapanır NE geçer; veri beklenir.")
    elif fo > 0 and flo > 0:
        print("\n  -> H2 GEÇTİ. Model kalabalığı yeniyor. Kol H3'e (para) ilerler.")
    else:
        neden = "fark sıfır ya da negatif" if fo <= 0 else "GA sıfırı içeriyor"
        print(f"\n  -> H2 DÜŞTÜ ({neden}). **ÇİFTE KOLU KAPANIR.** Kupon sistemi kurulmaz.")

    # ------------------------------ LOG-LOSS (madde 5) ----------------------------
    ll = {}
    for k in ("bot2", "kamu"):
        v = []
        for a, b, wa, wb, d in olay:
            pa = a["p"][k].get(wa, 1e-9)
            pb = b["p"][k].get(wb, 1e-9)
            v.append(-np.log(max(pa * pb, 1e-12)))
        ll[k] = np.array(v)
    dll = ll["bot2"] - ll["kamu"]
    b = boot(dll)
    print("\n" + "-" * 100)
    print("  İKİNCİ OKUMA (madde 5 — hüküm ÜRETMEZ): ÇİFTE log-loss, düşük olan iyi")
    print(f"     model (bot2) {ll['bot2'].mean():.4f}   ·   kamu {ll['kamu'].mean():.4f}   ·   "
          f"fark {dll.mean():+.4f} [{np.percentile(b,5):+.4f} .. {np.percentile(b,95):+.4f}]")
    print("     (negatif fark = model daha iyi)")
    print("\n  UYARI (madde 6): yukarıdaki MUTLAK ROI'ler oynanabilir DEĞİLDİR — ayak 2'nin")
    print("  olasılıkları kapanış oranından türetiliyor, kupon ise ayak 1'den önce alınıyor.")
    print("  Her iki kol da aynı biçimde sızıntılı olduğu için FARK adildir; seviyeler değil.")


if __name__ == "__main__":
    main()
