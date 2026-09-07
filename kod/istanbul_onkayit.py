# -*- coding: utf-8 -*-
"""
istanbul_onkayit.py — BEKLEYENLER #11'in ÖN-KAYITLI SINAMASI (K122'de yazılan ölçüt).
SALT-OKUNUR: hiçbir dosyaya yazmaz.

=====================================================================================
ÖLÇÜT — 26 AĞUSTOS 2026'DA, SONUÇ GÖRÜLMEDEN YAZILDI. BURADA DEĞİŞTİRİLMEDİ.
(BEKLEYENLER.md #11'den birebir kopya:)

  H       : İstanbul'da kamu-fark'ımız diğer pistlerdekinden DÜŞÜKTÜR.
  Ölçüm   : ≥400 YENİ İstanbul ayağı biriktiğinde, pist_analiz.py'nin kıyas birimiyle
            + olay-bootstrap ile (İstanbul farkı − diğer farkı) hesaplanır.
  DOĞRULANDI : ancak ve ancak %95 GA TAMAMEN sıfırın altındaysa.
  DÜŞER / KOL KAPANIR : GA sıfırı içeriyorsa.
  Karar sınırı: doğrulansa BİLE "İstanbul oynamayalım" DEĞİL — yapılacak iş MEKANİZMAYI
            ölçmektir (hipotez: havuz derinliği ↑ → piyasa verimliliği ↑, K112).
=====================================================================================

NEDEN BU BETİK AYRI: `pist_analiz.py` BETİMLEYİCİDİR ve TÜM veriye bakar; #11 ise yalnız
K122'den SONRA birikene bakmak zorundadır (desen post-hoc görüldü; aynı veriyle sınanamaz).
Kıyas birimi `pist_analiz.kamu_kiyas`'tan İÇE AKTARILIR — ikinci bir kopya yazmak,
"ölçü sessizce değişti mi?" sorusunu doğurur.

BOOTSTRAP BİÇİMİ (önceden sabit): iki grup (İstanbul olayları / diğer olaylar) BAĞIMSIZ
tabakalardır ve boyutları tasarımla sabittir → her tabaka KENDİ İÇİNDE yeniden örneklenir.
Birim OLAYDIR (tarih,pist,seq), ayak değil: aynı Altılı'nın 6 ayağı bağımsız değildir.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
from pist_analiz import yukle, kamu_kiyas                          # noqa: E402

BASLANGIC = "2026-08-26"        # K122'nin yazıldığı gün; SONRASI "yeni veri"
HEDEF = 400                     # ön-kayıtlı tetik
TEKRAR = 10000
TOHUM = 20260907


def main():
    k, a, _tem, _med = yukle()
    k = kamu_kiyas(k, a)
    k = k[k["kamu_tuttu"].notna()].copy()

    yeni = k[k["tarih"] > BASLANGIC].copy()
    ist_ayak = int((yeni["pist"] == "ISTANBUL").sum())

    print("=" * 100)
    print("BEKLEYENLER #11 — İSTANBUL AYKIRISI: ÖN-KAYITLI SINAMA (K122)")
    print("=" * 100)
    print(f"  pencere            : {BASLANGIC} SONRASI (K122 kararından sonra biriken)")
    print(f"  yeni İstanbul ayağı: {ist_ayak} / {HEDEF} "
          f"{'✓ tetik DOLU' if ist_ayak >= HEDEF else '✗ tetik dolmadı — DUR'}")
    if ist_ayak < HEDEF:
        print("  Ölçüt gereği sınama YAPILMAZ. (Erken bakmak ön-kaydı bozar.)")
        return 1
    print(f"  eşleşebilen toplam ayak: {len(yeni):,} "
          f"(kıyas: aynı ayak, aynı genişlik, kamu cetvelinin ilk n'i)")

    yeni["fark"] = yeni["tuttu"].astype(float) - yeni["kamu_tuttu"].astype(float)
    yeni["ist"] = yeni["pist"] == "ISTANBUL"
    yeni["olay"] = list(zip(yeni["tarih"], yeni["pist"], yeni["seq"]))

    # ---------------------------------------------------------------- betimleyici
    print("\n" + "-" * 100)
    print("  BETİMLEYİCİ (ön-kayıtlı ölçüt bunlara BAKMADAN yazılmıştı)")
    print("-" * 100)
    print(f"  {'grup':>12} {'ayak':>7} {'biz':>8} {'kamu':>8} {'fark(puan)':>12} {'olay':>6}")
    for ad, s in (("İSTANBUL", yeni[yeni.ist]), ("DİĞER", yeni[~yeni.ist])):
        print(f"  {ad:>12} {len(s):>7} {'%'+f'{100*s.tuttu.mean():.1f}':>8} "
              f"{'%'+f'{100*s.kamu_tuttu.mean():.1f}':>8} "
              f"{100*s.fark.mean():>+12.2f} {s.olay.nunique():>6}")
    for p, g in yeni[~yeni.ist].groupby("pist"):
        print(f"     └─ {p:>9} {len(g):>7} {'%'+f'{100*g.tuttu.mean():.1f}':>8} "
              f"{'%'+f'{100*g.kamu_tuttu.mean():.1f}':>8} {100*g.fark.mean():>+12.2f}")

    # ---------------------------------------------------------------- test
    def delta(df):
        i, d = df[df.ist], df[~df.ist]
        if not len(i) or not len(d):
            return np.nan
        return 100 * (i.fark.mean() - d.fark.mean())

    gozlenen = delta(yeni)
    grup = {o: g for o, g in yeni.groupby("olay")}
    ist_olay = [o for o in grup if grup[o]["ist"].iloc[0]]
    dig_olay = [o for o in grup if not grup[o]["ist"].iloc[0]]

    rng = np.random.default_rng(TOHUM)
    boot = np.empty(TEKRAR)
    for t in range(TEKRAR):
        s1 = rng.choice(len(ist_olay), len(ist_olay))
        s2 = rng.choice(len(dig_olay), len(dig_olay))
        df = pd.concat([grup[ist_olay[i]] for i in s1] + [grup[dig_olay[i]] for i in s2])
        boot[t] = delta(df)
    alt, ust = np.percentile(boot, [2.5, 97.5])

    print("\n" + "=" * 100)
    print("  SINAMA: δ = (İstanbul farkı) − (diğer farkı),  puan")
    print("=" * 100)
    print(f"  gözlenen δ    : {gozlenen:+.2f} puan")
    print(f"  %95 GA (olay-bootstrap, {TEKRAR:,} tekrar, tabakalı): "
          f"[{alt:+.2f}, {ust:+.2f}]")
    print(f"  δ<0 olan tekrar oranı: %{100*(boot < 0).mean():.1f}")
    print(f"\n  K122'de gözlenen (post-hoc, ESKİ veri): −6,0 [−10,2, −1,7]")

    print("\n" + "=" * 100)
    if ust < 0:
        print("  HÜKÜM: **DOĞRULANDI** — GA tamamen sıfırın altında.")
        print("  Ön-kayıt gereği yapılacak iş: MEKANİZMA ölçümü (havuz derinliği → verimlilik).")
        print("  'İstanbul oynamayalım' SONUCU ÇIKMAZ — ölçüt bunu açıkça dışlıyor.")
    else:
        print("  HÜKÜM: **DÜŞTÜ — KOL KAPANIR.** GA sıfırı içeriyor.")
        print("  K122'nin deseni YENİ veride tekrarlanmadı → post-hoc desen olarak kalır.")
        print("  Yeniden açılması için yeni MEKANİZMA iddiası + yeni veri gerekir (Kural 6/K33).")
    print("=" * 100)
    return 0


if __name__ == "__main__":
    sys.exit(main())
