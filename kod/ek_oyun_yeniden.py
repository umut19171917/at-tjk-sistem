# -*- coding: utf-8 -*-
"""
ek_oyun_yeniden.py — SORU (kullanıcı, 8 Eyl 2026, `ek_oyun_ikili.py`nin devamı):
"5'li/4'lü oynayacaksak, Altılı'nın seçimlerini kopyalamak yerine BÜTÇEYİ 5 (veya 4) AYAĞA
YENİDEN DAĞITSAYDIK ne olurdu?"

SALT-OKUNUR: hiçbir dosyaya yazmaz.

`ek_oyun_ikili.py` "aynı seçimler, ayak düşür" senaryosunu ölçtü. Bu betik dağıtıcıyı
5 ve 4 ayak için YENİDEN ÇALIŞTIRIR — açgözlü dağıtıcı 5 ayakta farklı bir kupon kurar.

--------------------------------------------------------------------------------------
ÇAPA TESTİ (K33: ölçmeden önce bilinen değeri yeniden üret)
--------------------------------------------------------------------------------------
Karşı-olgusalı hesaplamadan ÖNCE, aynı boru hattıyla GERÇEK 6 ayaklı kupon yeniden kurulur
ve canlıda yazılmış `secim` ile karşılaştırılır. Eşleşme yüksek değilse kurulum bozuktur ve
5/4 ayaklı sayılar OKUNMAZ. Bu kapı geçilmeden sonuç basılmaz.

--------------------------------------------------------------------------------------
İKİ BÜTÇE TANIMI — ikisi de raporlanır, çünkü "aynı bütçe" belirsiz bir ifade
--------------------------------------------------------------------------------------
  A) AYNI KOMBO TAVANI : config'in kendi tavanı (900 kombo) 5/4 ayağa dağıtılır.
                         Dağıtıcı için "doğal" bütçe. Ama birim fiyat yüksek olduğu için
                         HARCANAN PARA ARTAR (900 x 1,50 = 1.350 vs 900 x 1,25 = 1.125).
  B) AYNI TL BÜTÇE     : o olayda 6'lıya harcanan TL kadar para. K108'in kuralı
                         ("bütçe Altılı ile eşitlenerek — yoksa kıyas anlamsız olur").
                         max_kombo = floor(6'lı bedeli / o ürünün birim fiyatı).

Puan kaynağı ve zamanı config'in KENDİsinden alınır (KONFIG): acgozlu900_15 -> bot2 @15 dk,
bot1_900 -> bot1 @30 dk. Dağıtıcı ikisinde de `acgozlu`.

KAPSAM UYARISI: kupon-anı fotoğrafı her olayda tam değil (K111: %78). Fotoğrafı eksik olan
olay ATLANIR ve sayısı raporlanır. Bu yüzden buradaki olay sayısı `ek_oyun_ikili.py`den
DAHA AZDIR; iki betiğin toplamları doğrudan kıyaslanamaz — kıyas AYNI olay kümesi üzerinde,
aşağıdaki "eşleşmiş kıyas" bölümünde yapılır.
"""
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
import rapor_ortak as ro                                            # noqa: E402
from altili_canli import KONFIG                                     # noqa: E402

CONFIGLER = ["acgozlu900_15", "bot1_900"]
BIRIM = {6: None, 5: 1.50, 4: 1.75}          # 6 -> pist tarifesi
ILK_GUN = "2026-07-20"
CIZGI = "=" * 104


def bolum(b):
    print("")
    print(CIZGI)
    print("  " + b)
    print(CIZGI)


def acgozlu_n(ayak_atlari, max_kombo):
    """kupod_kur_acgozlu'nun n-ayaklı hâli. Mantık BİREBİR aynı (K65):
    her ayakta 1 atla başla; kazanç/bedel oranı en yüksek atı ekle."""
    sr = [sorted([(no, p) for no, p in a if pd.notna(p) and p > 0], key=lambda x: -x[1])
          for a in ayak_atlari]
    m = len(sr)
    if any(len(s) == 0 for s in sr):
        return None
    k = [1] * m
    P = [s[0][1] for s in sr]
    while True:
        kombo = int(np.prod(k))
        en_iyi, en_oran = None, 0.0
        for j in range(m):
            if k[j] >= len(sr[j]):
                continue
            if kombo // k[j] * (k[j] + 1) > max_kombo:
                continue
            p = sr[j][k[j]][1]
            bedel = math.log((k[j] + 1) / k[j])
            oran = (math.log1p(p / P[j]) / bedel) if (P[j] > 0 and bedel > 0) else 0.0
            if oran > en_oran:
                en_oran, en_iyi = oran, j
        if en_iyi is None:
            break
        j = en_iyi
        P[j] += sr[j][k[j]][1]
        k[j] += 1
    return [set(no for no, _ in sr[j][:k[j]]) for j in range(m)]


def yukle():
    k = pd.read_csv(KOK / "veri" / "altili_kupon.csv", low_memory=False)
    k = k[k["config"].isin(CONFIGLER) & k["tuttu"].notna()].copy()
    for c in ("nat", "tuttu", "race_kod", "seq", "ayak", "kazanan"):
        k[c] = pd.to_numeric(k[c], errors="coerce")
    k = k[k["nat"].notna() & k["nat"].gt(0)]

    a = pd.read_csv(KOK / "veri" / "altili_kupon_ani.csv", low_memory=False)
    for c in ("bot1", "bot2", "no", "dk_grup", "seq", "ayak"):
        a[c] = pd.to_numeric(a[c], errors="coerce")
    a["dk_grup"] = a["dk_grup"].fillna(30)

    t = pd.read_csv(KOK / "veri" / "altili_temettu.csv")
    t["seq"] = pd.to_numeric(t["seq"], errors="coerce")
    tem = {(r.tarih, r.pist, int(r.seq)): float(r.temettu)
           for r in t.itertuples() if pd.notna(r.temettu) and pd.notna(r.seq)}

    n = pd.read_csv(KOK / "veri" / "nli_ganyan.csv", low_memory=False)
    n = n[n["urun"].isin([4, 5]) & (n["tarih"] >= ILK_GUN)].copy()
    n["ayaklar"] = n["race_kodlar"].astype(str).apply(
        lambda s: frozenset(int(x) for x in s.split("/") if x.strip().isdigit()))
    return k, a, tem, n


def main():
    k, a, tem, n = yukle()
    ani = {key: g for key, g in a.groupby(["tarih", "pist", "seq", "dk_grup", "ayak"])}

    capa_ayni = capa_top = 0
    kayit, atlanan_foto = [], 0

    for (tar, pist, seq, cfg), g in k.groupby(["tarih", "pist", "seq", "config"]):
        g = g.sort_values("ayak")
        if len(g) != 6:
            continue
        konf = KONFIG[cfg]
        puan, dk, tavan = konf.get("puan", "bot2"), float(konf.get("dk", 30)), konf["kombo"]

        # --- kupon ani fotografi (6 ayak da olmali)
        atlar, ok = {}, True
        for _, L in g.iterrows():
            key = (tar, pist, int(seq), dk, int(L["ayak"]))
            s = ani.get(key)
            if s is None or s[puan].isna().all():
                ok = False
                break
            s = s.dropna(subset=[puan])
            atlar[int(L["ayak"])] = list(zip(s["no"].astype(int), s[puan].astype(float)))
        if not ok:
            atlanan_foto += 1
            continue

        tut = dict(zip(g["ayak"].astype(int), g["tuttu"].astype(int)))
        kaz = dict(zip(g["ayak"].astype(int), g["kazanan"]))
        rk2ayak = dict(zip(g["race_kod"].astype(int), g["ayak"].astype(int)))
        gercek = {int(r.ayak): set(int(x) for x in str(r.secim).split(",") if x.strip())
                  for r in g.itertuples()}

        # --- CAPA: 6 ayakli kuponu yeniden kur
        y6 = acgozlu_n([atlar[i] for i in range(1, 7)], tavan)
        if y6 is None:
            atlanan_foto += 1
            continue
        for i in range(6):
            capa_top += 1
            capa_ayni += (y6[i] == gercek[i + 1])

        b6 = int(np.prod([len(s) for s in y6])) * ro.birim_fiyat(pist)
        h6 = all((kaz[i + 1] in y6[i]) for i in range(6))
        olay = f"{tar}|{pist}|{int(seq)}|{cfg}"
        kayit.append(dict(cfg=cfg, urun=6, senaryo="A", olay=olay, bedel=b6,
                          odul=tem.get((tar, pist, int(seq)), 0.0) if h6 else 0.0, tuttu=h6))
        # 6'li B senaryosunda da aynidir (bütçe zaten kendisi)
        kayit.append(dict(cfg=cfg, urun=6, senaryo="B", olay=olay, bedel=b6,
                          odul=tem.get((tar, pist, int(seq)), 0.0) if h6 else 0.0, tuttu=h6))

        # --- 5'li / 4'lu : urunun GERCEK ayaklariyla, YENIDEN dagitilarak
        aday = n[(n["tarih"] == tar) & (n["sehir"] == pist)]
        for urun in (5, 4):
            sec = [r for r in aday[aday["urun"] == urun].itertuples()
                   if r.ayaklar and len(r.ayaklar) == urun
                   and all(x in rk2ayak for x in r.ayaklar)]
            if not sec:
                continue
            r = sec[0]
            ayak_no = sorted(rk2ayak[x] for x in r.ayaklar)
            liste = [atlar[i] for i in ayak_no]

            # --- K: KOPYALA (ek_oyun_ikili.py'nin senaryosu) — AYNI olay kümesinde temel
            nat_g = dict(zip(g["ayak"].astype(int), g["nat"].astype(int)))
            bedel_k = int(np.prod([nat_g[i] for i in ayak_no])) * BIRIM[urun]
            hit_k = all(tut[i] == 1 for i in ayak_no)
            kayit.append(dict(cfg=cfg, urun=urun, senaryo="K", olay=olay, bedel=bedel_k,
                              odul=(float(r.tl) if (hit_k and str(r.tip) != "devir") else 0.0),
                              tuttu=hit_k))

            for senaryo, mk in (("A", tavan), ("B", int(b6 // BIRIM[urun]))):
                y = acgozlu_n(liste, mk)
                if y is None:
                    continue
                bedel = int(np.prod([len(s) for s in y])) * BIRIM[urun]
                hit = all(kaz[i] in s for i, s in zip(ayak_no, y))
                odul = (float(r.tl) if (hit and str(r.tip) != "devir") else 0.0)
                kayit.append(dict(cfg=cfg, urun=urun, senaryo=senaryo, olay=olay,
                                  bedel=bedel, odul=odul, tuttu=hit))

    # ------------------------------------------------------------------ CAPA KAPISI
    oran = 100 * capa_ayni / capa_top if capa_top else 0
    print(CIZGI)
    print("EK OYUN — BÜTÇE 5/4 AYAĞA YENİDEN DAĞITILSAYDI")
    print(CIZGI)
    print(f"  ÇAPA TESTİ: kupon-anı fotoğrafından yeniden kurulan 6 ayaklı kupon, canlıda")
    print(f"  yazılan seçimle AYNI mı?   {capa_ayni:,}/{capa_top:,} ayak = %{oran:.1f}")
    if oran < 90:
        print(f"  *** ÇAPA GEÇMEDİ (%90 altı) — kurulum güvenilmez, sonuç BASILMIYOR. ***")
        return 1
    print(f"  ÇAPA GEÇTİ. Kupon-anı fotoğrafı eksik olduğu için atlanan olay: {atlanan_foto}")

    d = pd.DataFrame(kayit)
    d["urun_ad"] = d["urun"].map({6: "6'lı Altılı", 5: "5'li ganyan", 4: "4'lü ganyan"})

    for sen, ad in (("A", "SENARYO A — aynı KOMBO tavanı (900) 5/4 ayağa dağıtılıyor"),
                    ("B", "SENARYO B — aynı TL bütçe (6'lıya harcanan para kadar)")):
        s = d[d.senaryo == sen]
        bolum(ad)
        print(f"  {'':<18}{'fırsat':>7}{'tutan':>7}{'oran':>8}{'bedel':>12}"
              f"{'ödül':>12}{'NET':>12}{'ROI':>9}")
        print("  " + "-" * 100)
        for u, g in s.groupby("urun_ad", sort=False):
            b, o, t = g.bedel.sum(), g.odul.sum(), int(g.tuttu.sum())
            print(f"  {u:<18}{len(g):>7}{t:>7}{'%' + f'{100*t/len(g):.1f}':>8}"
                  f"{b:>12,.0f}{o:>12,.0f}{o-b:>+12,.0f}{'%' + f'{100*(o-b)/b:.1f}':>9}")
        b, o = s.bedel.sum(), s.odul.sum()
        print("  " + "-" * 100)
        print(f"  {'TOPLAM':<18}{len(s):>7}{int(s.tuttu.sum()):>7}{'':>8}"
              f"{b:>12,.0f}{o:>12,.0f}{o-b:>+12,.0f}{'%' + f'{100*(o-b)/b:.1f}':>9}")

    # ------------------------------------------------------------------ eslesmis kiyas
    bolum("EŞLEŞMİŞ KIYAS — AYNI olaylarda: kopyala vs yeniden dağıt (yalnız 5'li + 4'lü)")
    yan = d[d.urun != 6]
    print(f"  {'':<34}{'bilet':>7}{'tutan':>7}{'bedel':>12}{'ödül':>12}{'NET':>12}{'ROI':>9}")
    print("  " + "-" * 100)
    for sen, ad in (("K", "KOPYALA · Altılı seçimleri aynen"),
                    ("A", "yeniden dağıt · aynı kombo tavanı"),
                    ("B", "yeniden dağıt · aynı TL bütçe")):
        g = yan[yan.senaryo == sen]
        b, o = g.bedel.sum(), g.odul.sum()
        print(f"  {ad:<34}{len(g):>7}{int(g.tuttu.sum()):>7}{b:>12,.0f}{o:>12,.0f}"
              f"{o-b:>+12,.0f}{'%' + f'{100*(o-b)/b:.1f}':>9}")

    bolum("ÜRÜN BAZINDA EŞLEŞMİŞ KIYAS")
    print(f"  {'':<12}{'senaryo':<26}{'tutan':>7}{'bedel':>12}{'ödül':>12}"
          f"{'NET':>12}{'ROI':>9}")
    print("  " + "-" * 100)
    for u in ("5'li ganyan", "4'lü ganyan"):
        for sen, ad in (("K", "kopyala"), ("A", "yeniden · kombo tavanı"),
                        ("B", "yeniden · TL bütçe")):
            g = yan[(yan.urun_ad == u) & (yan.senaryo == sen)]
            b, o = g.bedel.sum(), g.odul.sum()
            print(f"  {u if sen == 'K' else '':<12}{ad:<26}"
                  f"{int(g.tuttu.sum()):>3}/{len(g):<3}{b:>12,.0f}{o:>12,.0f}"
                  f"{o-b:>+12,.0f}{'%' + f'{100*(o-b)/b:.1f}':>9}")
        print("  " + "-" * 100)

    bolum("TEK BİLET BAĞIMLILIĞI — en büyük İKİ ödül çıkarılınca")
    for sen, ad in (("K", "kopyala"), ("A", "yeniden · kombo tavanı"),
                    ("B", "yeniden · TL bütçe")):
        g = yan[yan.senaryo == sen]
        b, o = g.bedel.sum(), g.odul.sum()
        en2 = g[g.tuttu].odul.nlargest(2).sum()
        print(f"  {ad:<26} ham ROI %{100*(o-b)/b:+7.1f}  ·  en büyük 2 = ödülün "
              f"%{100*en2/o if o else 0:.0f}'i  ·  onlar çıkınca ROI %{100*(o-en2-b)/b:+.1f}")

    bolum("MEKANİZMA — geniş kupon daha çok tutturur ama HER İSABET DAHA UCUZ (K98-h kalıbı)")
    print(f"  {'senaryo':<26}{'isabet':>8}{'ort. at/ayak':>14}{'ort. temettü/isabet':>22}")
    print("  " + "-" * 100)
    for sen, ad in (("K", "kopyala"), ("A", "yeniden · kombo tavanı"),
                    ("B", "yeniden · TL bütçe")):
        g = yan[yan.senaryo == sen]
        v = g[g.tuttu]
        gen = (g.bedel / g.urun.map(BIRIM)).apply(np.log) / g.urun
        print(f"  {ad:<26}{len(v):>8}{np.exp(gen.mean()):>14.2f}"
              f"{v.odul.mean() if len(v) else 0:>22,.0f}")
    print(CIZGI)
    return 0


if __name__ == "__main__":
    sys.exit(main())
