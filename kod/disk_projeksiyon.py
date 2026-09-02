# -*- coding: utf-8 -*-
"""
disk_projeksiyon.py — K146 / BEKLEYENLER 22-E: DİSK BÜYÜME PROJEKSİYONU. SALT-OKUNUR.

SORU: veri 1,4 GB. Ne kadar hızlı büyüyor, ne zaman sıkışır? Bilinmezse sürpriz kesinti riski.

YÖNTEM — İKİ HIZ AYRI ÖLÇÜLÜR (tek ortalama yanıltıcı):
  (a) ARŞİV (veri/ham): 2021'den beri birikiyor -> geçmiş ortalama ileriyi de temsil eder,
      çünkü yarış takvimi yıllar arası benzer.
  (b) GÜNLÜK YAZANLAR (defter, kupon, oran_log, temettü): yalnız ~2 aylık -> geçmiş
      TOPLAM ortalama bunları HAFİFE ALIR. Kendi ömürlerinden ölçülür.
Toplam ileri hız = (a) + (b). Geçmiş ortalamayla kıyası da basılır ki fark görünsün.

NOT: `.git` de büyür ama izlenen içerik küçük (ham ve büyük CSV'ler .gitignore'da);
ayrı satır olarak gösterilir.
"""
import os
from datetime import date
from pathlib import Path

KOK = Path(__file__).resolve().parent.parent
ARSIV_BASLANGIC = date(2021, 1, 1)          # ham arşivin kapsadığı ilk yarış
GUNLUK_BASLANGIC = date(2026, 7, 1)         # defter/kupon akışının başladığı gün (K42)
DISK_GB = 40                                # Hetzner CX22 gibi bir hedef; senaryo için


def boyut(p: Path) -> int:
    if p.is_dir():
        return sum((Path(r) / f).stat().st_size
                   for r, _, fs in os.walk(p) for f in fs)
    return p.stat().st_size if p.exists() else 0


def main():
    bugun = date.today()
    ham = boyut(KOK / "veri" / "ham")
    veri = boyut(KOK / "veri")
    git = boyut(KOK / ".git")
    rapor = boyut(KOK / "raporlar")
    kod = boyut(KOK / "kod")
    toplam = veri + git + rapor + kod

    # gunluk yazanlar = veri/ (ham + turetilen buyuk CSV'ler haric)
    turetilen = sum(boyut(KOK / "veri" / f) for f in ("katilim.csv", "ozellikli.csv"))
    gunluk = veri - ham - turetilen

    g_arsiv = (bugun - ARSIV_BASLANGIC).days
    g_gunluk = max((bugun - GUNLUK_BASLANGIC).days, 1)

    hiz_ham = ham / g_arsiv                       # bayt/gun
    hiz_gunluk = gunluk / g_gunluk
    hiz_turetilen = turetilen / g_arsiv           # ham'dan uretiliyor -> ham hiziyla olcekli
    ileri = hiz_ham + hiz_gunluk + hiz_turetilen
    gecmis_ort = toplam / g_arsiv

    print("=" * 92)
    print(f"K146 / 22-E — DİSK BÜYÜME PROJEKSİYONU   ({bugun:%d %b %Y})")
    print("=" * 92)
    print(f"  {'bileşen':>32} {'boyut':>11} {'ömür':>8} {'hız':>13}")
    print("-" * 92)
    for ad, b, g in (("veri/ham (JSON arşivi)", ham, g_arsiv),
                     ("türetilen CSV (katilim+ozellikli)", turetilen, g_arsiv),
                     ("günlük yazanlar (defter/kupon/log)", gunluk, g_gunluk),
                     (".git", git, g_arsiv),
                     ("raporlar + kod", rapor + kod, g_arsiv)):
        print(f"  {ad:>32} {b/1e6:>9.1f} MB {g:>6} g {b/g/1e6:>10.3f} MB/g")
    print("-" * 92)
    print(f"  {'TOPLAM':>32} {toplam/1e6:>9.1f} MB")

    print(f"\n  geçmiş ortalama hız : {gecmis_ort*365.25/1e6:>6.0f} MB/yıl  "
          "(yanıltıcı — günlük akış yalnız 2 aylık)")
    print(f"  İLERİ hız (düzeltilmiş): {ileri*365.25/1e6:>6.0f} MB/yıl")
    print(f"    · arşiv      {hiz_ham*365.25/1e6:>6.0f} MB/yıl")
    print(f"    · türetilen  {hiz_turetilen*365.25/1e6:>6.0f} MB/yıl")
    print(f"    · günlük     {hiz_gunluk*365.25/1e6:>6.0f} MB/yıl  "
          f"({hiz_gunluk/hiz_ham:.1f}× arşiv hızı)")

    print("\n" + "-" * 92)
    print(f"  {'yıl':>5} {'toplam (MB)':>13} {'toplam (GB)':>13}   {DISK_GB} GB diskin yüzdesi")
    print("-" * 92)
    for y in (1, 2, 3, 5, 10):
        t = (toplam + ileri * 365.25 * y) / 1e6
        pct = 100 * t / (DISK_GB * 1000)
        bar = "#" * int(pct / 3)
        print(f"  +{y:>3} {t:>13,.0f} {t/1000:>13.1f}   %{pct:>5.1f}  {bar}")

    kalan_gb = DISK_GB * 1e9 - toplam
    yil_dolu = kalan_gb / (ileri * 365.25)
    print(f"\n  {DISK_GB} GB dolma süresi: ~{yil_dolu:.0f} yıl "
          f"(~{bugun.year + int(yil_dolu)})")

    print("\n" + "=" * 92)
    print("HÜKÜM")
    print("=" * 92)
    if yil_dolu > 10:
        print(f"  Disk SORUN DEĞİL. Mevcut hızla {DISK_GB} GB ~{yil_dolu:.0f} yıl yeter;")
        print("  projenin ufku (25 Eylül karar noktası) bunun yanında ölçülemeyecek kadar kısa.")
        print("  22-G'de önerilen sıkıştırma/arşivleme işi ŞİMDİ GEREKSİZ.")
    else:
        print(f"  DİKKAT: {DISK_GB} GB ~{yil_dolu:.0f} yılda dolar. Sıkıştırma planı gerekli.")
    print("\n  Asıl risk disk DEĞİL, TEK KOPYA: veri/ham (1,1 GB) git dışında ve tek diskte.")
    print("  TJK arşivi kapanırsa kazi.py ile yeniden inmiyor -> ZAMANLI #6 (dış yedek) asıl iş.")


if __name__ == "__main__":
    main()
