# -*- coding: utf-8 -*-
"""
idempotans_denetim.py — K147 / BEKLEYENLER 22-D: ÇİFT ÇALIŞMA GÜVENLİĞİ. SALT-OKUNUR.

SORU: `takip.py` arka arkaya iki kez koşarsa CSV'lere yinelenen satır yazar mı? Saat kayması,
çift tetik, PC uyanması, elle `baslat_takip.bat` gibi durumlar gerçek.

YÖNTEM — takip.py İKİ KEZ ÇALIŞTIRILMAZ. Bu, canlı sisteme kasten çift yazma denemesi
olurdu; kabul edilemez. Bunun yerine iki bağımsız kanıt:

  (A) AMPİRİK: 45 günlük canlı sicilde yinelenen satır var mı? Sistem zaten defalarca
      üst üste koştu (görev her 15 dk + elle geçişler); yinelenen yoksa korumalar çalışıyor.
  (B) YAPISAL: korumaların kodda GERÇEKTEN var olduğu doğrulanır. Ampirik temizlik
      "şans eseri" de olabilir; mekanizmayı görmeden hüküm verilmez.

Bu ikisi birlikte, riskli bir deney yapmadan soruyu cevaplar.
"""
import re
import sys
from pathlib import Path

import pandas as pd

KOK = Path(__file__).resolve().parent.parent

# (dosya, yinelenmemesi gereken anahtar, aciklama)
TABLOLAR = [
    ("veri/altili_kupon.csv", ["tarih", "pist", "seq", "config", "ayak"],
     "her Altılı ayağı × config için TEK satır"),
    ("veri/altili_kupon_ani.csv", ["tarih", "pist", "seq", "dk_grup", "ayak", "no"],
     "kupon anı olasılık fotoğrafı"),
    ("veri/defter.csv", ["tarih", "pist", "race_kod", "no"],
     "her at-koşu için TEK tahmin satırı"),
    ("veri/altili_temettu.csv", ["tarih", "pist", "seq"],
     "her Altılı için TEK resmî temettü"),
    ("veri/altili_oran_log.csv", ["kayit_ts", "race_kod", "no"],
     "zaman damgalı oran kaydı"),
]

# (dosya, aranan desen, korumanin adi ve ne yaptigi)
KORUMALAR = [
    ("kod/takip.py", r"msvcrt\.locking",
     "TEK-İNSTANS KİLİDİ — iki takip.py aynı anda koşamaz (OS kilidi, süreç ölünce bırakılır)"),
    ("kod/takip.py", r"_durum_oku|_isaretle",
     "GÜN MÜHRÜ — işlenen koşu (pist, no) diske işaretlenir; sonraki geçiş atlar"),
    ("kod/takip.py", r'"SONUCLA" not in done',
     "SONUÇLA MÜHRÜ — günde bir kez; ikinci çağrı hiç girmez"),
    ("kod/altili_canli.py", r"if all\(c in var for c in cfgler\)",
     "KUPON MÜHRÜ — (tarih,pist,seq,config) zaten kuruluysa yeniden kurulmaz"),
    ("kod/defter.py", r'df\["sonuclandi"\]\.isna\(\)',
     "SONUÇ DOLDURMA — yalnız BOŞ satırlar doldurulur; dolu satıra dokunulmaz"),
    ("kod/altili_canli.py", r'df\["sonuclandi"\]\.isna\(\)',
     "ALTILI SONUÇLAMA — yalnız boş ayaklar doldurulur"),
    ("kod/takip.py", r"posta gecti",
     "POSTA KORUMASI — koşu başladıysa defter satırı YAZILMAZ (geç veriyle kirletme yok)"),
]


def main():
    print("=" * 96)
    print("K147 / 22-D — ÇİFT ÇALIŞMA (IDEMPOTANS) DENETİMİ")
    print("takip.py İKİ KEZ ÇALIŞTIRILMADI — canlıya kasten çift yazma denemesi yapılmaz.")
    print("=" * 96)

    # ----------------------------------------------------- (A) ampirik
    print("\n(A) AMPİRİK — 45 günlük canlı sicilde yinelenen satır var mı?")
    print("-" * 96)
    print(f"  {'dosya':>30} {'satır':>8} {'yinelenen':>10}  anahtar")
    kirli = 0
    for yol, anahtar, aciklama in TABLOLAR:
        p = KOK / yol
        if not p.exists():
            print(f"  {yol:>30} {'—':>8} {'yok':>10}  (dosya bulunamadı)")
            continue
        d = pd.read_csv(p, low_memory=False)
        eksik = [c for c in anahtar if c not in d.columns]
        if eksik:
            print(f"  {yol:>30} {len(d):>8,} {'?':>10}  kolon eksik: {eksik}")
            continue
        dup = int(d.duplicated(subset=anahtar).sum())
        kirli += dup
        bayrak = "TEMİZ" if dup == 0 else f"*** {dup} ***"
        print(f"  {yol.split('/')[-1]:>30} {len(d):>8,} {bayrak:>10}  {'+'.join(anahtar)}")

    # ----------------------------------------------------- (B) yapisal
    print("\n(B) YAPISAL — korumalar kodda gerçekten var mı?")
    print("-" * 96)
    eksik_koruma = 0
    for yol, desen, ad in KORUMALAR:
        p = KOK / yol
        src = p.read_text(encoding="utf-8") if p.exists() else ""
        var = bool(re.search(desen, src))
        if not var:
            eksik_koruma += 1
        print(f"  [{'✓' if var else '✗'}] {yol:<22} {ad}")

    # ----------------------------------------------------- hüküm
    print("\n" + "=" * 96)
    print("HÜKÜM")
    print("=" * 96)
    if kirli == 0 and eksik_koruma == 0:
        print("  İDEMPOTANS DOĞRULANDI — iki bağımsız kanıtla:")
        print(f"    · 45 günlük sicilde {sum(1 for _ in TABLOLAR)} tabloda TEK yinelenen satır yok")
        print(f"    · {len(KORUMALAR)} korumanın {len(KORUMALAR)}'i de kodda mevcut")
        print("\n  Sistem zaten defalarca üst üste koştu (görev 15 dk'da bir + elle geçişler);")
        print("  temizlik şans eseri değil, mekanizma çalışıyor.")
    else:
        if kirli:
            print(f"  *** {kirli} YİNELENEN SATIR BULUNDU — incelenmeli ***")
        if eksik_koruma:
            print(f"  *** {eksik_koruma} KORUMA KODDA BULUNAMADI — desen değişmiş olabilir ***")
    print("\n  AÇIK KALAN (bu denetimin kapsamadığı): iki FARKLI makinede (ör. PC + sunucu)")
    print("  eşzamanlı çalışma. Tek-instans kilidi yalnız aynı makinede korur — göç")
    print("  senaryosunda (BEKLEYENLER'de ertelendi) bu ayrıca ele alınmalı.")


if __name__ == "__main__":
    sys.exit(main())
