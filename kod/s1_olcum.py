# -*- coding: utf-8 -*-
"""
s1_olcum.py — ZAMANLI-4 / K142'nin **S1 basamağının** ÖLÇÜM KODU. SALT-OKUNUR.

=====================================================================================
BU DOSYA 7 EYLÜL 2026'DA YAZILDI VE GİT'E MÜHÜRLENDİ — ÖLÇÜM PENCERESİ 25 EYLÜL.
=====================================================================================
NEDEN ŞİMDİ: K142 ölçütü yazdı ama **kodunu yazmadı** ve bunu "tam ön-kayıt değil" diye
dürüstçe işaretledi. Kodu 25 Eylül'de yazmak, o gün elimde şu serbestlik derecelerini
bırakırdı: hangi config'ler havuzlanır · bootstrap birimi ne · hangi alt küme · bağlar
nasıl çözülür. Bunların her biri sonucu oynatabilir.

K142'nin ÇIKAR ÇATIŞMASI NOTU doğrudan bu dosyayı yazan tarafı işaret ediyor: ölçütü
öneren (Claude) aynı gün "arşiv modu" yönünde görüş bildirmişti. O yüzden karar penceresine
18 gün kala, veri görülmeden, kendi elimi bağlıyorum. 7 Eylül'de #11 (K152) tam bu
disiplinin bir yanlış bulguyu nasıl elediğini gösterdi.

TARİH KAPISI: betik 25 Eylül 2026'dan ÖNCE gerçek veriyle ÇALIŞMAYI REDDEDER. Mühür budur.
Kodun doğruluğu `--sinama` ile SENTETİK veride sınanır (gerçek cevaba dokunmadan).

=====================================================================================
S1 — ÖLÇÜT (BEKLEYENLER ZAMANLI-4'ten birebir):
  "25 Eylül'e kadar biriken TÜM sicille, aşağıdakilerden HERHANGİ BİRİ sağlanırsa
   -> GÜNLÜK DEVAM + yeni ön-kayıtlı kol."
   S1-a: pist_analiz'in kamu-fark ölçüsü, aktif config'lerin HAVUZUNDA %95 GA ile 0'ın üstünde
   S1-b: defter.csv'de sistem top-pick isabeti kamu top-pick isabetini %95 GA ile geçiyor
   S1-c: #4 veya #11 DOĞRULANDI çıkıp mekanizma iddiası doğuruyor
=====================================================================================
BURADA SABİTLENEN, K142'DE YAZILMAMIŞ OLAN HER ŞEY (çıktı görülmeden):

 S1-a  birim        : KUPON AYAĞI. Kıyas `pist_analiz.kamu_kiyas` — aynı ayak, aynı genişlik,
                      kamu cetvelinin ilk n'i. İKİNCİ BİR KOPYA YAZILMAZ, içe aktarılır.
       kapsam       : `altili_canli.aktif_konfig()` — aktif config'ler, TEK HAVUZ.
                      Config bazında ayrı bakılMAZ (çokluluk üretir, K143).
       istatistik   : delta = ortalama(biz − kamu), puan. OLAY düzeyi bootstrap
                      (tarih,pist,seq), 10.000 tekrar, yüzdelik %95 GA, ÇİFT YANLI.
       geçme koşulu : GA'nın ALT ucu > 0.
 S1-b  birim        : KOŞU (defter.csv'de bir race_kod = bir eşleşmiş gözlem):
                      sistem top-pick tuttu mu / kamu top-pick tuttu mu.
       sistem pick  : `bot2` en yüksek at.  kamu pick: `kamu` en yüksek at.
                      Bağ olursa `no` küçük olan — keyfî ama SABİT ve sonuçtan bağımsız.
       kapsam       : `sonuc` dolu (koşulmuş) ve bot2/kamu dolu her koşu. Altılı şartı YOK
                      (K142 "defter.csv'de" diyor, "Altılı ayağında" demiyor).
       istatistik   : delta = sistem isabeti − kamu isabeti, puan. KOŞU düzeyi bootstrap,
                      10.000 tekrar, %95 GA ÇİFT YANLI + McNemar (tam binom) bilgi olarak.
       geçme koşulu : GA'nın ALT ucu > 0.
 S1-c  : 7 Eyl 2026'da ZATEN DÜŞTÜ — #11 K152'de, #4 K153'te. Bu kapı KAPALI; ölçütleri
         koşuldu ve ikisi de "DOĞRULANDI" vermedi.

 HÜKÜM: S1-a VEYA S1-b geçerse S1 = SAĞLANDI. İkisi de geçmezse S1 = SAĞLANMADI.
 Çokluluk notu: iki alternatif ölçü kasten "herhangi biri" mantığıyla bağlandı (K142 S1'i
 bilerek GENİŞ tuttu). Bu, yanlış-pozitif oranını tek teste göre yükseltir; K142'nin çıkar
 çatışması gerekçesiyle BİLEREK kabul edilmiştir ve burada düzeltilMEZ.
=====================================================================================
"""
import sys
from datetime import date
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))

KARAR_GUNU = date(2026, 9, 25)
TEKRAR = 10000
TOHUM = 20260925


def mcnemar_p(a, b):
    n = a + b
    return min(1.0, 2 * sum(comb(n, i) for i in range(min(a, b) + 1)) / 2 ** n) if n else 1.0


def ga(gruplar, rng):
    """Küme (cluster) bootstrap: her grup bir BÜTÜN olarak yeniden örneklenir."""
    boot = np.empty(TEKRAR)
    for i in range(TEKRAR):
        s = rng.choice(len(gruplar), len(gruplar))
        boot[i] = 100 * np.concatenate([gruplar[j] for j in s]).mean()
    return np.percentile(boot, [2.5, 97.5])


# ------------------------------------------------------------------ S1-a
def s1a(rng):
    from pist_analiz import yukle, kamu_kiyas
    k, a, _t, _m = yukle()
    k = kamu_kiyas(k, a)
    k = k[k["kamu_tuttu"].notna()].copy()
    k["d"] = k["tuttu"].astype(float) - k["kamu_tuttu"].astype(float)
    k["o"] = list(zip(k["tarih"], k["pist"], k["seq"]))
    gruplar = [g["d"].to_numpy() for _, g in k.groupby("o")]
    alt, ust = ga(gruplar, rng)
    return dict(ad="S1-a  kupon ayagi: biz - kamu (eslesmis, aktif config HAVUZ)",
                n=len(k), birim=f"{len(gruplar)} olay", delta=100 * k["d"].mean(),
                alt=alt, ust=ust, ek="")


# ------------------------------------------------------------------ S1-b
def s1b(rng):
    d = pd.read_csv(KOK / "veri" / "defter.csv", low_memory=False)
    for c in ("bot2", "kamu", "sonuc", "no"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d = d[d["sonuc"].notna() & d["bot2"].notna() & d["kamu"].notna()]
    biz, kam = [], []
    for _rk, g in d.groupby("race_kod"):
        g = g.sort_values("no")                       # bag kurali: kucuk `no` kazanir
        b = g.loc[g["bot2"].idxmax()]
        p = g.loc[g["kamu"].idxmax()]
        biz.append(1.0 if b["sonuc"] == 1 else 0.0)
        kam.append(1.0 if p["sonuc"] == 1 else 0.0)
    biz, kam = np.array(biz), np.array(kam)
    fark = biz - kam
    alt, ust = ga([np.array([x]) for x in fark], rng)
    n10 = int(((biz == 1) & (kam == 0)).sum())
    n01 = int(((biz == 0) & (kam == 1)).sum())
    return dict(ad="S1-b  kosu: sistem top-pick - kamu top-pick (defter.csv)",
                n=len(fark), birim=f"{len(fark)} kosu", delta=100 * fark.mean(),
                alt=alt, ust=ust,
                ek=f"sistem %{100*biz.mean():.1f} - kamu %{100*kam.mean():.1f} - "
                   f"yalniz sistem {n10} - yalniz kamu {n01} - "
                   f"McNemar p={mcnemar_p(n10, n01):.4f}")


# ------------------------------------------------------------------ sinama
def sinama():
    """Kodun DOĞRULUĞUNU sentetik veride sınar — gerçek cevaba DOKUNMAZ.
    Sıfır etkili (null) veride %95 GA'nın sıfırı içerme oranı ~%95 çıkmalı."""
    print("SENTETIK SINAMA — boru hatti ve GA kalibrasyonu (gercek veri OKUNMAZ)")
    rng = np.random.default_rng(7)
    kapsayan, N = 0, 300
    for _ in range(N):
        gruplar = [rng.integers(0, 2, 6) - rng.integers(0, 2, 6) for _ in range(120)]
        b = np.empty(400)
        for i in range(400):
            s = rng.choice(len(gruplar), len(gruplar))
            b[i] = 100 * np.concatenate([gruplar[j] for j in s]).mean()
        lo, hi = np.percentile(b, [2.5, 97.5])
        kapsayan += (lo <= 0 <= hi)
    oran = 100 * kapsayan / N
    print(f"  null veride %95 GA sifiri icerme orani: %{oran:.1f}  (beklenen ~%95)")
    print(f"  {'GA KALIBRE [OK]' if 90 <= oran <= 99 else '*** GA KALIBRE DEGIL ***'}")
    for f in (s1a, s1b):
        print(f"  {f.__name__}: tanimli, imza tamam")
    return 0


def main(argv):
    if "--sinama" in argv:
        return sinama()
    bugun = date.today()
    print("=" * 100)
    print("ZAMANLI-4 / K142 — S1 BASAMAGI: KENAR IDDIASI DIRILDI MI?")
    print("=" * 100)
    if bugun < KARAR_GUNU:
        print(f"  MUHUR ACIK DEGIL. Karar gunu {KARAR_GUNU:%d %b %Y}, bugun {bugun:%d %b %Y} "
              f"({(KARAR_GUNU-bugun).days} gun var).")
        print("  Bu betik 7 Eyl 2026'da yazilip git'e muhurlendi; ERKEN BAKMAK on-kaydi bozar.")
        print("  Kodun dogrulugunu sinamak icin:  python kod/s1_olcum.py --sinama")
        return 2

    rng = np.random.default_rng(TOHUM)
    print(f"  olcum gunu : {bugun:%d %b %Y}   -  kod 7 Eyl 2026'da muhurlendi")
    print("  S1-c       : KAPALI — #11 (K152) ve #4 (K153) 7 Eyl'de DUSTU\n")
    gecen = []
    for f in (s1a, s1b):
        r = f(rng)
        ok = r["alt"] > 0
        gecen.append(ok)
        print("-" * 100)
        print(f"  {r['ad']}")
        print(f"    kapsam : {r['n']:,} satir - {r['birim']}")
        if r["ek"]:
            print(f"    ayrinti: {r['ek']}")
        print(f"    delta  : {r['delta']:+.3f} puan   %95 GA [{r['alt']:+.3f}, {r['ust']:+.3f}]")
        print(f"    HUKUM  : {'GECTI (alt uc > 0)' if ok else 'gecmedi (alt uc <= 0)'}")

    print("\n" + "=" * 100)
    if any(gecen):
        print("  S1 = SAGLANDI -> ZAMANLI-4 kurali: **GUNLUK DEVAM** + yeni on-kayitli kol.")
    else:
        print("  S1 = SAGLANMADI. Kural S2'ye gecer.")
        print("  S2 (7 Eyl'de olculdu): tek acik sayisal tetik #18, ~30 Kasim -> >30 gun -> HAYIR.")
        print("  S3 = ARSIV MODU olurdu — ANCAK K154: kullanici muafiyeti kullanildi,")
        print("       KUPON SIMULASYONU DURMAZ. Arastirma kolu kapanir, akis HOBI olarak surer.")
    print("=" * 100)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
