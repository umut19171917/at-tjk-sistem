# -*- coding: utf-8 -*-
"""
pist_analiz.py — ŞEHİR (PİST) BAZINDA SİCİL (K122). Salt offline, hiçbir dosyaya YAZMAZ.

Kullanıcı: "bildiğimiz koşuları ve tutan altılıları şehir bazında hiç ölçmedik."
Doğru — bu eksen hiç bakılmamıştı.

======================================================================================
ÖNCE ÇERÇEVE: BU ÖLÇÜM BETİMLEYİCİDİR, KARAR ÜRETMEZ
======================================================================================
5 pist × birkaç ölçüt bakılıyor. Şans eseri birinin "iyi" çıkması KAÇINILMAZDIR
(K107'nin FDR notu). Bu yüzden ölçüm baştan şöyle çerçeveleniyor:

  >> "Şu pistte iyiyiz, oraya yoğunlaşalım" DENMEZ. Böyle bir karar için önce
     ön-kayıtlı bir ölçüt yazılmalı, sonra YENİ veriyle sınanmalıdır (K33/K52).
     Buradaki sayılar hipotez ÜRETİR, hipotez DOĞRULAMAZ.

  >> Bonferroni referansı: 5 pist için α=0,05'in karşılığı p<0,010'dur. Tablolarda
     ham p basılıyor; bu eşiği geçmeyen hiçbir fark "bulgu" sayılmaz.

ÜÇ AYRI ÖLÇÜ (K109'un iskeleti — ham isabet TEK BAŞINA okunmaz):
  1. HAM   : isabet/ayak — pist zorluğunu VE kupon genişliğini birlikte taşır
  2. ADİL  : aynı ayakta, aynı sayıda atla KAMU ne tuttururdu? (fark = seçim becerisi)
  3. PARA  : bedel vs resmî temettü. Altılı'da YALNIZ 6/6 öder, o yüzden ham ROI tek bir
     büyük ödemeyle savrulur ve pistleri kıyaslamaya ELVERİŞSİZDİR. Kıyaslanabilir ölçü
     BAŞABAŞ 6/6 EŞİĞİDİR: o pistin medyan temettüsüyle, harcanan parayı çıkarmak için
     kuponların yüzde kaçının 6/6 tutması gerekirdi.

CONFOUNDER: K88 saha büyüklüğünün isabeti belirlediğini ölçtü (saha 4-7 → 12+ geçişinde
isabet %65,4 → %36,4). Pistler farklı saha dağılımlarına sahipse "pist etkisi" sandığımız
şey saha etkisi olabilir. Bu yüzden saha büyüklüğü hem pist bazında basılıyor hem de
4. bölümde saha kovası İÇİNDE kıyas yapılıyor.
"""
import sys
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
import rapor_ortak as ro                                          # noqa: E402
from altili_canli import aktif_konfig, KONFIG                      # noqa: E402

BONFERRONI = 0.010          # 5 pist icin duzeltilmis esik


def mcnemar_p(a, b):
    n = a + b
    return min(1.0, 2 * sum(comb(n, i) for i in range(min(a, b) + 1)) / 2 ** n) if n else 1.0


def yukle():
    k = pd.read_csv(KOK / "veri" / "altili_kupon.csv", low_memory=False)
    k = k[k["sonuclandi"].notna() & k["tuttu"].notna() & k["config"].isin(aktif_konfig())]
    for c in ("nat", "tuttu", "kazanan", "race_kod", "seq"):
        k[c] = pd.to_numeric(k[c], errors="coerce")
    k = k[k["nat"].notna() & k["nat"].gt(0)]
    k["dk"] = k["config"].map(lambda c: KONFIG[c].get("dk", 30))

    a = pd.read_csv(KOK / "veri" / "altili_kupon_ani.csv", low_memory=False)
    if "dk_grup" not in a.columns:
        a["dk_grup"] = 30
    for c in ("kamu", "no", "race_kod", "dk_grup", "seq"):
        a[c] = pd.to_numeric(a[c], errors="coerce")
    a["dk_grup"] = a["dk_grup"].fillna(30)

    t = pd.read_csv(KOK / "veri" / "altili_temettu.csv", low_memory=False)
    t["seq"] = pd.to_numeric(t["seq"], errors="coerce")
    t["temettu"] = pd.to_numeric(t["temettu"], errors="coerce")
    tem = {(r.tarih, r.pist, int(r.seq)): (r.temettu if pd.notna(r.temettu) else 0.0)
           for r in t.itertuples() if pd.notna(r.seq)}
    medyan = t.groupby("pist")["temettu"].median().to_dict()
    return k, a, tem, medyan


def kamu_kiyas(k, a):
    """ADIL: ayni ayak, ayni genislik, KAMU cetvelinin ilk k'si tutar miydi?"""
    ix = {key: g for key, g in a.groupby(["tarih", "pist", "seq", "dk_grup", "race_kod"])}
    kt, saha = [], []
    for r in k.itertuples():
        g = ix.get((r.tarih, r.pist, int(r.seq), float(r.dk), int(r.race_kod)))
        if g is None or g["kamu"].isna().all():
            kt.append(np.nan)
            saha.append(np.nan)
            continue
        g = g.dropna(subset=["kamu"])
        ilk = set(g.sort_values("kamu", ascending=False)["no"].head(int(r.nat)).astype(int))
        kt.append(1.0 if r.kazanan in ilk else 0.0)
        saha.append(len(g))
    k = k.copy()
    k["kamu_tuttu"] = kt
    k["saha"] = saha
    return k


def b(baslik):
    print("\n" + "=" * 104)
    print(baslik)
    print("=" * 104)


def main():
    k, a, tem, medyan = yukle()
    k = kamu_kiyas(k, a)

    print("=" * 104)
    print("K122 — ŞEHİR BAZINDA SİCİL. Betimleyicidir; karar üretmez (5 pist -> Bonferroni p<0,010).")
    print(f"  sonuçlanmış ayak: {len(k):,} | aktif config: {len(aktif_konfig())} | "
          f"tarih: {k.tarih.min()} .. {k.tarih.max()}")
    print("=" * 104)

    # ---------------------------------------------------------------- 1
    b("1) AYAK DÜZEYİ — üç ölçü yan yana")
    print(f"  {'pist':>10} {'ayak':>6} {'ort.saha':>9} {'ort.gen':>8} {'HAM':>7} "
          f"{'ADİL: kamu':>11} {'FARK':>7} {'yalnız-biz':>11} {'yalnız-kamu':>12} {'p':>8}")
    sat = []
    for p, g in k.groupby("pist"):
        gk = g[g["kamu_tuttu"].notna()]
        if len(gk) < 30:
            continue
        biz = gk["tuttu"].astype(bool)
        kam = gk["kamu_tuttu"].astype(bool)
        a_only, b_only = int((biz & ~kam).sum()), int((~biz & kam).sum())
        sat.append((p, len(g), g["saha"].mean(), g["nat"].mean(), 100 * g["tuttu"].mean(),
                    100 * kam.mean(), 100 * (biz.mean() - kam.mean()),
                    a_only, b_only, mcnemar_p(a_only, b_only)))
    for p, n, sh, gen, ham, kam, fk, ao, bo, pv in sorted(sat, key=lambda x: -x[6]):
        yildiz = " *" if pv < BONFERRONI else ""
        print(f"  {p:>10} {n:>6} {sh:>9.1f} {gen:>8.2f} {'%' + f'{ham:.1f}':>7} "
              f"{'%' + f'{kam:.1f}':>11} {fk:>+7.1f} {ao:>11} {bo:>12} {pv:>8.3f}{yildiz}")
    print("\n  HAM = kendi isabetimiz (pist zorluğu + kupon genişliği birlikte)")
    print("  ADİL = aynı ayakta aynı sayıda atla KAMU'nun isabeti · FARK = seçim becerisi")
    print(f"  * = Bonferroni eşiğini (p<{BONFERRONI}) geçen fark. Yıldız yoksa BULGU YOK.")

    # ---------------------------------------------------------------- 2
    b("2) SAHA BÜYÜKLÜĞÜ DAĞILIMI (K88 karıştırıcısı)")
    print(f"  {'pist':>10} {'ort.saha':>9} {'saha<=8':>9} {'saha 9-11':>10} "
          f"{'saha>=12':>9} {'HAM isabet':>11}")
    for p, g in k.groupby("pist"):
        s = g["saha"].dropna()
        if len(s) < 30:
            continue
        print(f"  {p:>10} {s.mean():>9.1f} {'%' + f'{100 * (s <= 8).mean():.0f}':>9} "
              f"{'%' + f'{100 * ((s >= 9) & (s <= 11)).mean():.0f}':>10} "
              f"{'%' + f'{100 * (s >= 12).mean():.0f}':>9} "
              f"{'%' + f'{100 * g.tuttu.mean():.1f}':>11}")

    # ---------------------------------------------------------------- 3
    b("3) SAHA KOVASI İÇİNDE — pist farkı saha etkisinden mi geliyor?")
    gk = k[k["kamu_tuttu"].notna()].copy()
    gk["biz"] = gk["tuttu"].astype(bool)
    gk["kam"] = gk["kamu_tuttu"].astype(bool)
    for lo, hi, ad in [(0, 8, "saha<=8"), (9, 11, "saha 9-11"), (12, 99, "saha>=12")]:
        s = gk[(gk["saha"] >= lo) & (gk["saha"] <= hi)]
        for p, g in s.groupby("pist"):
            if len(g) < 60:
                continue
            print(f"  {ad:>10} {p:>10} {len(g):>6} biz {'%' + f'{100 * g.biz.mean():.1f}':>7} "
                  f"kamu {'%' + f'{100 * g.kam.mean():.1f}':>7} "
                  f"fark {100 * (g.biz.mean() - g.kam.mean()):>+6.1f}")
        print()
    print("  Bir pist ÜÇ kovada da aynı yöndeyse, fark saha etkisiyle AÇIKLANMIYOR demektir.")

    # ---------------------------------------------------------------- 4
    b("4) OLAY DÜZEYİ — 6/6 ve PARA (birim fiyat pistin kendi tarifesi)")
    print(f"  {'pist':>10} {'kupon':>6} {'6/6':>4} {'6/6 oranı':>10} {'bedel':>12} "
          f"{'ödül':>12} {'ROI':>8} {'medyan tem.':>13} {'BAŞABAŞ 6/6':>12}")
    for p, gp in k.groupby("pist"):
        birim = ro.birim_fiyat(p)
        bedel = odul = 0.0
        kupon = tam = 0
        for (t_, p_, s_, c_), g in gp.groupby(["tarih", "pist", "seq", "config"]):
            if len(g) != 6 or g["tuttu"].isna().any():
                continue
            bedel += int(np.prod(g["nat"])) * birim
            kupon += 1
            if g["tuttu"].sum() == 6:
                tam += 1
                odul += tem.get((t_, p_, int(s_)), 0.0)
        if not kupon:
            continue
        roi = (odul - bedel) / bedel * 100 if bedel else np.nan
        mt = medyan.get(p, np.nan)
        # BASABAS 6/6: o pistin medyan temettusuyle, harcanan parayi cikarmak icin
        # kuponlarin yuzde kacinin 6/6 tutmasi gerekirdi. Ham ROI tek buyuk odemeyle
        # savrulur; bu olcu savrulmaz -> pistleri KIYASLANABILIR kilan sutun budur.
        bb = (bedel / (kupon * mt) * 100) if (pd.notna(mt) and mt > 0) else np.nan
        print(f"  {p:>10} {kupon:>6} {tam:>4} {'%' + f'{100 * tam / kupon:.1f}':>10} "
              f"{bedel:>12,.0f} {odul:>12,.0f} {roi:>+7.1f}% {mt:>13,.0f} "
              f"{'%' + f'{bb:.1f}':>12}")
    print("\n  UYARI: ham ROI pistleri KIYASLAMAK için KULLANILAMAZ (tek 6/6 tabloyu savurur).")
    print("  Kıyaslanabilir okuma: GERÇEKLEŞEN 6/6 oranını BAŞABAŞ eşiğiyle karşılaştır.")
    print("  Gerçekleşen < başabaş -> o pistte kaybediyoruz (beklenen durum; kesinti %48,6).")

    # ---------------------------------------------------------------- 5
    b("5) PİST x AİLE — bot1 bazı pistlerde farklı mı davranıyor?")
    k2 = k.copy()
    k2["aile"] = k2["config"].map(lambda c: "BOT1" if KONFIG[c].get("puan") == "bot1" else "BOT2")
    print(f"  {'pist':>10} {'BOT1 ayak':>10} {'BOT1':>7} {'BOT2 ayak':>10} {'BOT2':>7} {'fark':>7}")
    for p in sorted(k2["pist"].unique()):
        g = k2[k2["pist"] == p]
        b1, b2 = g[g["aile"] == "BOT1"], g[g["aile"] == "BOT2"]
        if len(b1) < 20 or len(b2) < 20:
            continue
        print(f"  {p:>10} {len(b1):>10} {'%' + f'{100 * b1.tuttu.mean():.1f}':>7} "
              f"{len(b2):>10} {'%' + f'{100 * b2.tuttu.mean():.1f}':>7} "
              f"{100 * (b1.tuttu.mean() - b2.tuttu.mean()):>+7.1f}")
    print("\n  NOT: bot1 ve bot2 config'lerinin ortalama GENİŞLİKLERİ farklı ->")
    print("  bu sütunlar birbirinin adil kıyası DEĞİLDİR, yalnız pist içi desen gösterir.")


if __name__ == "__main__":
    main()
