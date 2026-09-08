# -*- coding: utf-8 -*-
"""
ek_oyun_ikili.py — SORU (kullanıcı, 8 Eyl 2026): "Yalnız `acgozlu900_15` ve `bot1_900` ile
kupon kurmuş olsaydık ve bu kuponların son 5 ayağına 5'Lİ, son 4 ayağına 4'LÜ GANYAN da
yatırmış olsaydık; 4'lü/5'li ve toplam kâr-zarar ne olurdu?"

SALT-OKUNUR: hiçbir dosyaya yazmaz.

K120'DEN FARKI: K120 aynı soruyu **tüm aktif config'ler** için ölçtü (410/338 fırsat).
Bu betik yalnız **iki config**e daraltıyor. Daraltma sonucu değiştirebilir: iki config'in
genişliği çok farklı (`acgozlu900_15` ~4 at/ayak, `bot1_900` ~2) ve `bot1_900` kalabalıktan
kopuk seçim yapıyor (K67/K96).

--------------------------------------------------------------------------------------
AYAK EŞLEŞTİRME — VARSAYIMLA DEĞİL, VERİYLE
--------------------------------------------------------------------------------------
"5'li = Altılı'nın son 5 ayağı" K120'de program feed'inden doğrulanmıştı. Burada yine de
VARSAYILMIYOR: `nli_ganyan.csv` her ürünün GERÇEK `race_kodlar`ını taşıyor. Eşleştirme,
ürünün ayak kümesinin Altılı'nın 6 ayağının ALT KÜMESİ olmasıyla yapılır. Alt küme değilse
o fırsat ATLANIR ve sayısı raporlanır — sessizce yanlış eşleşme olmasın.

(K85 tam bu noktada hata yapmıştı: `SIRALI 5'Lİ BAHİS` ayrı bir üründür — tek koşuda ilk 5.
K120 düzeltti. Alt küme kuralı o hatayı yapısal olarak imkânsız kılar.)

BULUNAN YAPISAL KISIT: 4'lü/5'li her Altılı'ya bağlı DEĞİL. Günde iki Altılı olan kartlarda
ürün çoğunlukla İKİNCİ Altılı'ya takılı. Ölçüldü: seq=2'de 89/91 eşleşiyor, seq=1'de 4'lü
yalnız 30/101. Yani "her kuponun yanına 4'lü de yatıralım" senaryosu FİİLEN mümkün değil;
betik yalnız ürünün GERÇEKTEN var olduğu fırsatları sayar.

--------------------------------------------------------------------------------------
BİRİM FİYATLAR (K120'de kayıtlı tarife)
--------------------------------------------------------------------------------------
  6'lı : rapor_ortak.birim_fiyat(pist) -> 1,25 TL (ELAZIG/SANLIURFA/DIYARBAKIR'da 1,00)
  5'li : 1,50 TL      4'lü : 1,75 TL
5'li/4'lü için pist ayrımı kayıtlı olmadığından K120'nin düz tarifesi kullanılır. Bu,
o pistlerde bedeli BİR MİKTAR YÜKSEK gösterebilir -> tahmin KÖTÜMSER yanlı, sonucu abartmaz.

DEVİR: `tip='devir'` olayda kimse tutturmamıştır; ödül 0 ve bizim tutturmamız tanım gereği
imkânsız. Ayrıca raporlanır.
ÖDÜL: resmî temettü (1 birim); tuttuğumuzda 1 birim kazanmış sayılırız (K120 ile aynı).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOK / "kod"))
import rapor_ortak as ro                                            # noqa: E402

CONFIGLER = ["acgozlu900_15", "bot1_900"]
BIRIM = {5: 1.50, 4: 1.75}
ILK_GUN = "2026-07-20"
TEKRAR = 10000
CIZGI = "=" * 104


def bolum(baslik):
    print("")
    print(CIZGI)
    print("  " + baslik)
    print(CIZGI)


def yukle():
    k = pd.read_csv(KOK / "veri" / "altili_kupon.csv", low_memory=False)
    k = k[k["config"].isin(CONFIGLER) & k["tuttu"].notna()].copy()
    for c in ("nat", "tuttu", "race_kod", "seq", "ayak"):
        k[c] = pd.to_numeric(k[c], errors="coerce")
    k = k[k["nat"].notna() & k["nat"].gt(0)]

    t = pd.read_csv(KOK / "veri" / "altili_temettu.csv")
    t["seq"] = pd.to_numeric(t["seq"], errors="coerce")
    tem = {(r.tarih, r.pist, int(r.seq)): float(r.temettu)
           for r in t.itertuples() if pd.notna(r.temettu) and pd.notna(r.seq)}

    n = pd.read_csv(KOK / "veri" / "nli_ganyan.csv", low_memory=False)
    n = n[n["urun"].isin([4, 5]) & (n["tarih"] >= ILK_GUN)].copy()
    n["ayaklar"] = n["race_kodlar"].astype(str).apply(
        lambda s: frozenset(int(x) for x in s.split("/") if x.strip().isdigit()))
    return k, tem, n


def topla(k, tem, n):
    kayit, atlanan, devir = [], {4: 0, 5: 0}, {4: 0, 5: 0}
    for (tar, pist, seq, cfg), g in k.groupby(["tarih", "pist", "seq", "config"]):
        g = g.sort_values("ayak")
        if len(g) != 6:
            continue
        altili = set(g["race_kod"].astype(int))
        nat = dict(zip(g["race_kod"].astype(int), g["nat"].astype(int)))
        tut = dict(zip(g["race_kod"].astype(int), g["tuttu"].astype(int)))
        olay = f"{tar}|{pist}|{int(seq)}|{cfg}"

        b6 = int(np.prod(list(nat.values()))) * ro.birim_fiyat(pist)
        h6 = all(tut.values())
        kayit.append(dict(cfg=cfg, urun=6, olay=olay, seq=int(seq), bedel=b6,
                          odul=tem.get((tar, pist, int(seq)), 0.0) if h6 else 0.0, tuttu=h6))

        aday = n[(n["tarih"] == tar) & (n["sehir"] == pist)]
        for urun in (5, 4):
            sec = [r for r in aday[aday["urun"] == urun].itertuples()
                   if r.ayaklar and r.ayaklar <= altili and len(r.ayaklar) == urun]
            if not sec:
                atlanan[urun] += 1
                continue
            r = sec[0]
            bedel = int(np.prod([nat[a] for a in r.ayaklar])) * BIRIM[urun]
            hit = all(tut[a] for a in r.ayaklar)
            if str(r.tip) == "devir":
                devir[urun] += 1
                odul = 0.0
            else:
                odul = float(r.tl) if hit else 0.0
            kayit.append(dict(cfg=cfg, urun=urun, olay=olay, seq=int(seq),
                              bedel=bedel, odul=odul, tuttu=hit))
    return pd.DataFrame(kayit), atlanan, devir


def tablo(df, baslik, anahtar):
    bolum(baslik)
    print(f"  {'':<18}{'fırsat':>7}{'tutan':>7}{'oran':>8}{'bedel':>12}"
          f"{'ödül':>12}{'NET':>12}{'ROI':>9}")
    print("  " + "-" * 100)
    for ad, g in df.groupby(anahtar, sort=False):
        b, o, t = g.bedel.sum(), g.odul.sum(), int(g.tuttu.sum())
        print(f"  {str(ad):<18}{len(g):>7}{t:>7}{'%' + f'{100*t/len(g):.1f}':>8}"
              f"{b:>12,.0f}{o:>12,.0f}{o-b:>+12,.0f}"
              f"{'%' + f'{100*(o-b)/b:.1f}' if b else '—':>9}")
    b, o = df.bedel.sum(), df.odul.sum()
    print("  " + "-" * 100)
    print(f"  {'TOPLAM':<18}{len(df):>7}{int(df.tuttu.sum()):>7}{'':>8}"
          f"{b:>12,.0f}{o:>12,.0f}{o-b:>+12,.0f}{'%' + f'{100*(o-b)/b:.1f}':>9}")


def roi_ga(g, rng):
    """Olay düzeyi bootstrap: aynı Altılı'nın 6'lı/5'li/4'lü bileti BİRLİKTE çekilir."""
    gr = [x[["bedel", "odul"]].to_numpy() for _, x in g.groupby("olay")]
    boot = np.empty(TEKRAR)
    for i in range(TEKRAR):
        s = np.concatenate([gr[j] for j in rng.integers(0, len(gr), len(gr))])
        boot[i] = 100 * (s[:, 1].sum() - s[:, 0].sum()) / s[:, 0].sum()
    return np.percentile(boot, [2.5, 97.5])


def main():
    k, tem, n = yukle()
    d, atlanan, devir = topla(k, tem, n)
    d["urun_ad"] = d["urun"].map({6: "6'lı Altılı", 5: "5'li ganyan", 4: "4'lü ganyan"})

    print(CIZGI)
    print("EK OYUN — YALNIZ acgozlu900_15 + bot1_900 ile: 6'LI + 5'Lİ + 4'LÜ")
    print(CIZGI)
    print(f"  kapsam : {int((d.urun==6).sum())} Altılı-kupon fırsatı  ·  {ILK_GUN} sonrası")
    print(f"  ürün YOK (o Altılı'ya 4'lü/5'li takılı değil): 5'li {atlanan[5]} · "
          f"4'lü {atlanan[4]}   ·   devir: 5'li {devir[5]} · 4'lü {devir[4]}")

    tablo(d, "ÜRÜN BAZINDA (iki config birlikte)", "urun_ad")
    for cfg in CONFIGLER:
        tablo(d[d.cfg == cfg], f"CONFIG: {cfg}", "urun_ad")

    rng = np.random.default_rng(20260908)
    bolum("ROI GÜVEN ARALIĞI — olay düzeyi bootstrap (10.000 tekrar)")
    for ad, g in list(d.groupby("urun_ad", sort=False)) + [("HEPSİ BİRLİKTE", d)]:
        alt, ust = roi_ga(g, rng)
        roi = 100 * (g.odul.sum() - g.bedel.sum()) / g.bedel.sum()
        durum = "sıfırı DIŞLIYOR" if (alt > 0 or ust < 0) else "sıfırı İÇERİYOR"
        print(f"  {ad:<16} ROI %{roi:+8.1f}   %95 GA [%{alt:+.1f}, %{ust:+.1f}]   {durum}")

    bolum("TEK BİLET BAĞIMLILIĞI — en büyük İKİ ödül çıkarılınca ne kalıyor?")
    for ad in ["6'lı Altılı", "5'li ganyan", "4'lü ganyan"]:
        g = d[d.urun_ad == ad]
        b, o = g.bedel.sum(), g.odul.sum()
        en2 = g[g.tuttu].odul.nlargest(2).sum()
        pay = 100 * en2 / o if o else 0
        print(f"  {ad:<14} ham ROI %{100*(o-b)/b:+7.1f}  ·  en büyük 2 ödül {en2:>10,.0f} TL "
              f"(ödülün %{pay:.0f}'i)  ·  onlar çıkınca ROI %{100*(o-en2-b)/b:+.1f}")
    for cfg in CONFIGLER + ["(ikisi birlikte)"]:
        g = d if cfg == "(ikisi birlikte)" else d[d.cfg == cfg]
        b, o = g.bedel.sum(), g.odul.sum()
        en2 = g[g.tuttu].odul.nlargest(2).sum()
        pay = 100 * en2 / o if o else 0
        print(f"  {cfg:<14} ham ROI %{100*(o-b)/b:+7.1f}  ·  en büyük 2 ödül {en2:>10,.0f} TL "
              f"(ödülün %{pay:.0f}'i)  ·  onlar çıkınca ROI %{100*(o-en2-b)/b:+.1f}")
    print(CIZGI)


if __name__ == "__main__":
    main()
